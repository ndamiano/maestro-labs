"""Play a landed sheet back as GIFs — one per (anim, dir), plus a grid of all of them."""
import argparse, json
from pathlib import Path
from PIL import Image
import numpy as np


def frames_of(sheet, m, anim, d):
    cw, ch = m["cell"]["w"], m["cell"]["h"]
    spec = m["anims"][anim]
    row = spec["rows"][d]
    return [sheet.crop((i * cw, row * ch, (i + 1) * cw, (row + 1) * ch))
            for i in range(spec["frames"])]


def delta(fs):
    g = [np.asarray(f.convert("L"), dtype=int) for f in fs]
    return max(np.abs(a - b).mean() for a, b in zip(g, g[1:]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    sheet = Image.open(args.sheet).convert("RGBA")
    m = json.loads(Path(args.sheet).with_suffix(".json").read_text())
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    warned = {w.split(":")[0] for w in m.get("warnings") or []}
    anims, dirs = list(m["anims"]), m["dirs"]
    cw, ch = m["cell"]["w"], m["cell"]["h"]
    n = max(s["frames"] for s in m["anims"].values())
    grid = []
    for i in range(n):
        canvas = Image.new("RGBA", (cw * len(dirs), ch * len(anims)), (24, 22, 28, 255))
        for r, a in enumerate(anims):
            for c, d in enumerate(dirs):
                fs = frames_of(sheet, m, a, d)
                canvas.alpha_composite(fs[i % len(fs)], (c * cw, r * ch))
        grid.append(canvas.convert("P", palette=Image.ADAPTIVE))
    fps = list(m["anims"].values())[0]["fps"]
    grid[0].save(out / "all.gif", save_all=True, append_images=grid[1:],
                 duration=int(1000 / fps), loop=0)
    print(f"{'anim/dir':16s} {'delta':>7s}  worker")
    for a in anims:
        for d in dirs:
            fs = frames_of(sheet, m, a, d)
            bg = [Image.new("RGBA", (cw, ch), (24, 22, 28, 255)) for _ in fs]
            comp = [Image.alpha_composite(b, f).convert("P", palette=Image.ADAPTIVE)
                    for b, f in zip(bg, fs)]
            comp[0].save(out / f"{a}_{d}.gif", save_all=True, append_images=comp[1:],
                         duration=int(1000 / m["anims"][a]["fps"]), loop=0)
            print(f"{a + '/' + d:16s} {delta(fs):7.2f}  {'WEAK' if f'{a}/{d}' in warned else ''}")


if __name__ == "__main__":
    main()
