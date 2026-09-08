#!/usr/bin/env python3
"""One character still -> a directional animated sprite sheet via MiniMax-H3 I2V on ComfyUI."""
from __future__ import annotations

import argparse
import io
import json
import time
import urllib.request
import uuid
from dataclasses import dataclass, field
from pathlib import Path

import av
import numpy as np
from PIL import Image

COMFY_INPUT_DIR = Path.home() / "comfy" / "mess-with-comfy" / "input"
CELL_H = 128
DIRS = ["front", "right", "back", "left"]
ANIM_SPEC = {
    "walk": {"length": 73, "cells": 16, "fps": 12},
    "idle": {"length": 22, "cells": 8, "fps": 8},
    "attack": {"length": 73, "cells": 16, "fps": 16},
}
ANIM_PROMPT = {
    "walk": "the character walks in place, legs alternating, arms swinging, no camera movement, plain white background, consistent character, 2D game sprite, never turns around",
    "idle": "the character breathes and shifts weight, subtle idle, stays in place, no camera movement, plain white background, consistent character, 2D game sprite",
    "attack": "the character performs a quick melee attack with the weapon, a big readable swing, then returns exactly to the starting pose, no camera movement, plain white background, consistent character, 2D game sprite",
}
DIR_SUFFIX = {"front": "", "right": ", seen from the side", "back": ", seen from behind", "left": ", seen from the side"}
TOUR_PROMPT = (
    "2D game character sprite on a plain white background. The character walks in place facing "
    "the camera for two steps, then turns to face right and walks in place for two steps, then "
    "turns to face away from the camera and walks in place for two steps, then turns to face left "
    "and walks in place for two steps, then turns back to face the camera. No camera movement, "
    "character stays centered, consistent character design, plain white background."
)
WEAK_MOTION_THRESHOLD = 15.0


def prep_still(src: Path, size: int = 768) -> Image.Image:
    img = Image.open(src).convert("RGBA")
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    bg.alpha_composite(img)
    flat = bg.convert("RGB")
    side = max(flat.size)
    square = Image.new("RGB", (side, side), (255, 255, 255))
    square.paste(flat, ((side - flat.width) // 2, (side - flat.height) // 2))
    return square.resize((size, size), Image.LANCZOS)


def submit_still_to_comfy(img: Image.Image, name: str) -> str:
    filename = f"{name}.png"
    img.save(COMFY_INPUT_DIR / filename)
    return filename


def build_i2v_workflow(
    image_filename: str,
    prompt: str,
    length: int,
    pinned: bool,
    filename_prefix: str,
    seed: int = 42,
) -> dict:
    i2v_inputs = {
        "clip": ["2", 0],
        "vae": ["3", 0],
        "prompt": prompt,
        "width": 768,
        "height": 768,
        "length": length,
        "first_frame": ["4", 0],
    }
    if pinned:
        i2v_inputs["last_frame"] = ["4", 0]
    return {
        "prompt": {
            "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "minimax_h3_fl2va_pruned_int8_convrot.safetensors", "weight_dtype": "default"}},
            "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax"}},
            "3": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
            "4": {"class_type": "LoadImage", "inputs": {"image": image_filename}},
            "5": {"class_type": "MiniMaxH3ImageToVideo", "inputs": i2v_inputs},
            "6": {"class_type": "MiniMaxH3SigmaShift", "inputs": {"model": ["1", 0], "shift_video": 12.0, "shift_audio": 3.0}},
            "7": {"class_type": "BasicGuider", "inputs": {"model": ["6", 0], "conditioning": ["5", 0]}},
            "8": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
            "9": {"class_type": "BasicScheduler", "inputs": {"model": ["6", 0], "scheduler": "simple", "steps": 20, "denoise": 1.0}},
            "10": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
            "11": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["10", 0], "guider": ["7", 0], "sampler": ["8", 0], "sigmas": ["9", 0], "latent_image": ["5", 1]}},
            "12": {"class_type": "VAEDecode", "inputs": {"samples": ["11", 1], "vae": ["3", 0]}},
            "13": {"class_type": "CreateVideo", "inputs": {"images": ["12", 0], "fps": 24.0}},
            "14": {"class_type": "SaveVideo", "inputs": {"video": ["13", 0], "filename_prefix": filename_prefix, "format": "auto", "codec": "auto"}},
        }
    }


def submit_prompt(comfy_url: str, workflow: dict) -> str:
    client_id = str(uuid.uuid4())
    payload = json.dumps({"prompt": workflow["prompt"], "client_id": client_id}).encode()
    req = urllib.request.Request(f"{comfy_url}/prompt", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    if "prompt_id" not in result:
        raise RuntimeError(f"comfy rejected prompt: {result}")
    return result["prompt_id"]


def poll_history(comfy_url: str, prompt_id: str, timeout: float) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with urllib.request.urlopen(f"{comfy_url}/history/{prompt_id}") as resp:
            history = json.loads(resp.read())
        if prompt_id in history:
            entry = history[prompt_id]
            status = entry.get("status", {})
            if status.get("completed") is True or status.get("status_str") == "success":
                return entry
            if status.get("status_str") == "error":
                raise RuntimeError(f"comfy job {prompt_id} failed: {status}")
        time.sleep(2)
    raise TimeoutError(f"comfy job {prompt_id} did not finish within {timeout}s")


def fetch_output_video(comfy_url: str, history_entry: dict, dest: Path) -> Path:
    outputs = history_entry["outputs"]
    for node_output in outputs.values():
        for video in node_output.get("videos") or node_output.get("gifs") or node_output.get("images") or []:
            params = f"filename={video['filename']}&subfolder={video.get('subfolder', '')}&type={video.get('type', 'output')}"
            with urllib.request.urlopen(f"{comfy_url}/view?{params}") as resp:
                dest.write_bytes(resp.read())
            return dest
    raise RuntimeError(f"no video output found in {outputs}")


def decode_video(path: Path) -> list[np.ndarray]:
    frames = []
    with av.open(str(path)) as container:
        stream = container.streams.video[0]
        for frame in container.decode(stream):
            frames.append(frame.to_ndarray(format="rgb24"))
    return frames


def non_white_mask(frame: np.ndarray, tol: int = 30) -> np.ndarray:
    return np.any(frame.astype(int) < (255 - tol), axis=-1)


def frame_centroid_x(frame: np.ndarray) -> float:
    mask = non_white_mask(frame)
    if not mask.any():
        return frame.shape[1] / 2.0
    xs = np.where(mask)[1]
    return float(xs.mean())


def frame_diff(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.abs(a.astype(int) - b.astype(int)).mean())


@dataclass
class TourSignals:
    centroid_x: list[float]
    diff_prev: list[float]
    turn_score: list[float]
    turns: list[int]
    picks: dict[str, int]


def smooth(values: list[float], window: int = 5) -> np.ndarray:
    arr = np.array(values, dtype=float)
    kernel = np.ones(window) / window
    return np.convolve(arr, kernel, mode="same")


def analyze_tour(frames: list[np.ndarray], min_sep: int = 25) -> TourSignals:
    centroids = [frame_centroid_x(f) for f in frames]
    diffs = [0.0] + [frame_diff(frames[i - 1], frames[i]) for i in range(1, len(frames))]
    dcentroid = [0.0] + [abs(centroids[i] - centroids[i - 1]) for i in range(1, len(centroids))]
    width = frames[0].shape[1]
    norm_dc = smooth([d / width for d in dcentroid])
    norm_diff = smooth([d / 255.0 for d in diffs])
    turn_score = (norm_dc + norm_diff).tolist()

    turns: list[int] = []
    candidates = np.argsort(turn_score)[::-1]
    for idx in candidates:
        idx = int(idx)
        if all(abs(idx - t) >= min_sep for t in turns):
            turns.append(idx)
        if len(turns) == 4:
            break
    turns.sort()

    n = len(frames)
    if len(turns) < 4:
        bounds = [0] + [n * (i + 1) // 5 for i in range(4)] + [n]
    else:
        bounds = [0] + turns + [n]

    picks: dict[str, int] = {}
    for i, name in enumerate(DIRS):
        lo, hi = bounds[i], bounds[i + 1]
        if hi <= lo:
            hi = lo + 1
        seg = range(lo, min(hi, n))
        best = min(seg, key=lambda k: diffs[k] if k > lo else diffs[min(k + 1, n - 1)])
        picks[name] = best

    return TourSignals(centroids, diffs, turn_score, turns, picks)


def plot_tour_signals(signals: TourSignals, dest: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    ax[0].plot(signals.centroid_x, label="centroid_x")
    ax[0].legend()
    ax[1].plot(signals.diff_prev, label="diff_prev", alpha=0.5)
    ax[1].plot(signals.turn_score, label="turn_score")
    for t in signals.turns:
        ax[1].axvline(t, color="red", linestyle="--")
    for name, idx in signals.picks.items():
        ax[1].axvline(idx, color="green", linestyle=":")
        ax[1].annotate(name, (idx, 0))
    ax[1].legend()
    fig.tight_layout()
    fig.savefig(dest)
    plt.close(fig)


def frame_to_still(frame: np.ndarray, size: int = 768) -> Image.Image:
    return Image.fromarray(frame).resize((size, size), Image.LANCZOS)


def matte_alpha(frame: np.ndarray, tol: int = 30) -> Image.Image:
    h, w, _ = frame.shape
    is_white = np.all(frame.astype(int) >= (255 - tol), axis=-1)
    flood = np.zeros((h, w), dtype=bool)
    stack = [(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)]
    visited = np.zeros((h, w), dtype=bool)
    idx = 0
    while idx < len(stack):
        y, x = stack[idx]
        idx += 1
        if y < 0 or y >= h or x < 0 or x >= w or visited[y, x] or not is_white[y, x]:
            continue
        visited[y, x] = True
        flood[y, x] = True
        stack.extend([(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)])
    alpha = np.where(flood, 0, 255).astype(np.uint8)
    rgba = np.dstack([frame, alpha])
    return Image.fromarray(rgba, mode="RGBA")


def trim_frozen_tail(diffs: list[float], threshold: float = 2.0) -> int:
    end = len(diffs)
    while end > 1 and diffs[end - 1] < threshold:
        end -= 1
    return end


def downsample_indices(n: int, count: int) -> list[int]:
    if n <= count:
        return list(range(n)) + [n - 1] * (count - n)
    return [round(i * (n - 1) / (count - 1)) for i in range(count)]


def union_bbox(masks: list[np.ndarray], pad_frac: float = 0.04) -> tuple[int, int, int, int]:
    ys0, xs0, ys1, xs1 = [], [], [], []
    for m in masks:
        if not m.any():
            continue
        ys, xs = np.where(m)
        ys0.append(ys.min())
        xs0.append(xs.min())
        ys1.append(ys.max())
        xs1.append(xs.max())
    y0, x0, y1, x1 = min(ys0), min(xs0), max(ys1), max(xs1)
    h, w = y1 - y0, x1 - x0
    py, px = int(h * pad_frac), int(w * pad_frac)
    return max(0, y0 - py), max(0, x0 - px), y1 + py, x1 + px


@dataclass
class ClipResult:
    direction: str
    anim: str
    frames_rgba: list[Image.Image]
    diffs: list[float]
    trimmed_n: int
    weak_motion: bool


def process_clip(video_path: Path, direction: str, anim: str) -> ClipResult:
    frames = decode_video(video_path)
    diffs = [0.0] + [frame_diff(frames[i - 1], frames[i]) for i in range(1, len(frames))]
    trimmed_n = trim_frozen_tail(diffs)
    trimmed = frames[:trimmed_n]
    weak_motion = max(diffs[1:trimmed_n], default=0.0) <= WEAK_MOTION_THRESHOLD
    rgba_frames = [matte_alpha(f) for f in trimmed]
    return ClipResult(direction, anim, rgba_frames, diffs, trimmed_n, weak_motion)


def build_sheet(
    clips: dict[tuple[str, str], ClipResult],
    dirs: list[str],
    anims: list[str],
    cell_h: int = CELL_H,
) -> tuple[Image.Image, dict]:
    masks_by_key = {}
    all_masks = []
    for key, clip in clips.items():
        cell_indices = downsample_indices(clip.trimmed_n, ANIM_SPEC[clip.anim]["cells"])
        selected = [clip.frames_rgba[i] for i in cell_indices]
        masks = [np.array(f)[:, :, 3] > 0 for f in selected]
        masks_by_key[key] = (selected, masks)
        all_masks.extend(masks)

    y0, x0, y1, x1 = union_bbox(all_masks)
    bbox_w, bbox_h = x1 - x0, y1 - y0
    cell_w = round(cell_h * bbox_w / bbox_h)

    max_cols = max(ANIM_SPEC[a]["cells"] for a in anims)
    rows = [(d, a) for a in anims for d in dirs if (d, a) in clips]
    sheet = Image.new("RGBA", (cell_w * max_cols, cell_h * max(len(rows), 1)), (0, 0, 0, 0))

    manifest_anims: dict = {}
    for a in anims:
        row_map = {d: rows.index((d, a)) for d in dirs if (d, a) in rows}
        manifest_anims[a] = {
            "rows": row_map,
            "frames": ANIM_SPEC[a]["cells"],
            "fps": ANIM_SPEC[a]["fps"],
        }

    for row_idx, (d, a) in enumerate(rows):
        selected, _ = masks_by_key[(d, a)]
        for col_idx, frame in enumerate(selected):
            cropped = frame.crop((x0, y0, x1, y1)).resize((cell_w, cell_h), Image.LANCZOS)
            sheet.paste(cropped, (col_idx * cell_w, row_idx * cell_h), cropped)

    pivot = {"x": cell_w // 2, "y": cell_h}
    manifest = {
        "cell": {"w": cell_w, "h": cell_h},
        "dirs": dirs,
        "anims": manifest_anims,
        "pivot": pivot,
        "warnings": [f"weak motion: {d}/{a}" for (d, a), c in clips.items() if c.weak_motion],
    }
    return sheet, manifest


@dataclass
class TimingLog:
    stages: dict[str, float] = field(default_factory=dict)

    def record(self, name: str, seconds: float) -> None:
        self.stages[name] = seconds


def run_clip_job(comfy_url: str, image_filename: str, anim: str, direction: str, prefix: str) -> str:
    spec = ANIM_SPEC[anim]
    prompt_text = ANIM_PROMPT[anim] + DIR_SUFFIX[direction]
    workflow = build_i2v_workflow(image_filename, prompt_text, spec["length"], True, prefix)
    return submit_prompt(comfy_url, workflow)


def run_pipeline(still_path: Path, out_dir: Path, name: str, anims: list[str], dirs_n: int, comfy_url: str) -> TimingLog:
    timing = TimingLog()
    debug_dir = out_dir / f"{name}_debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    clips_dir = out_dir / "clips_raw"
    clips_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    prepped = prep_still(still_path)
    still_filename = submit_still_to_comfy(prepped, f"{name}_prep")
    timing.record("prep", time.time() - t0)

    t0 = time.time()
    tour_wf = build_i2v_workflow(still_filename, TOUR_PROMPT, 197, False, f"i2v/{name}_tour")
    tour_id = submit_prompt(comfy_url, tour_wf)
    tour_entry = poll_history(comfy_url, tour_id, 900)
    tour_path = debug_dir / f"{name}_tour.mp4"
    fetch_output_video(comfy_url, tour_entry, tour_path)
    timing.record("tour", time.time() - t0)

    t0 = time.time()
    tour_frames = decode_video(tour_path)
    signals = analyze_tour(tour_frames)
    plot_tour_signals(signals, debug_dir / f"{name}_tour_signals.png")
    dirs = DIRS[:dirs_n]
    still_filenames: dict[str, str] = {}
    for d in dirs:
        idx = signals.picks[d]
        still_img = frame_to_still(tour_frames[idx])
        still_out = out_dir / "stills" / f"{name}_{d}.png"
        still_out.parent.mkdir(parents=True, exist_ok=True)
        still_img.save(still_out)
        still_img_prepped = prep_still(still_out)
        still_filenames[d] = submit_still_to_comfy(still_img_prepped, f"{name}_{d}")
    timing.record("facing_stills", time.time() - t0)

    t0 = time.time()
    jobs: dict[tuple[str, str], str] = {}
    for d in dirs:
        for a in anims:
            prefix = f"i2v/{name}_{d}_{a}"
            jobs[(d, a)] = run_clip_job(comfy_url, still_filenames[d], a, d, prefix)
    timing.record("submit_clips", time.time() - t0)

    t0 = time.time()
    clips: dict[tuple[str, str], ClipResult] = {}
    failures: dict[str, str] = {}
    for (d, a), pid in jobs.items():
        try:
            entry = poll_history(comfy_url, pid, 900)
            clip_path = clips_dir / f"{name}_{d}_{a}.mp4"
            fetch_output_video(comfy_url, entry, clip_path)
            result = process_clip(clip_path, d, a)
            clips[(d, a)] = result
            diff_txt = debug_dir / f"{name}_{d}_{a}_motion.txt"
            diff_txt.write_text("\n".join(f"{i}\t{v:.3f}" for i, v in enumerate(result.diffs)))
        except Exception as exc:
            failures[f"{d}/{a}"] = str(exc)
    timing.record("clips", time.time() - t0)

    t0 = time.time()
    sheet, manifest = build_sheet(clips, dirs, anims)
    manifest["warnings"].extend(f"clip failed: {k}: {v}" for k, v in failures.items())
    sheet.save(out_dir / f"{name}.png")
    (out_dir / f"{name}.json").write_text(json.dumps(manifest, indent=2))
    for d in dirs:
        (out_dir / "stills" / f"{name}_{d}.png")
    timing.record("compose", time.time() - t0)

    timing.record("total", sum(timing.stages.values()))
    (debug_dir / "timing.json").write_text(json.dumps(timing.stages, indent=2))
    (debug_dir / "tour_picks.json").write_text(json.dumps({"turns": signals.turns, "picks": signals.picks}, indent=2))
    return timing


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--still", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--anims", default="walk,idle,attack")
    parser.add_argument("--dirs", type=int, default=4)
    parser.add_argument("--comfy", default="http://127.0.0.1:8188")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    anims = args.anims.split(",")
    timing = run_pipeline(args.still, args.out, args.name, anims, args.dirs, args.comfy)
    print(json.dumps(timing.stages, indent=2))


if __name__ == "__main__":
    main()
