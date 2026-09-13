"""Which turntable frame shows each facing, scored by CLIP instead of by geometry.

Geometry proxies (quarter marks, symmetry, silhouette width) each failed on some body plan:
a back view is as symmetric as a front, and a horse is widest side-on where a person is
narrowest. CLIP is asked the question directly, per frame.
"""
import glob, json, os, re, sys, time
import numpy as np
import torch, open_clip
from PIL import Image

PROMPTS = {
    "front": ["a character seen from the front, facing the viewer, face and chest visible"],
    "side":  ["a character seen from the side, strict profile view, facing the edge of the frame"],
    "back":  ["a character seen from behind, back view, the back of the head and body visible"],
}


def load():
    model, _, pre = open_clip.create_model_and_transforms(
        "ViT-L-14", pretrained="laion2b_s32b_b82k", device="cuda")
    tok = open_clip.get_tokenizer("ViT-L-14")
    return model.eval(), pre, tok


def scores(frames, model, pre, tok):
    keys = list(PROMPTS)
    text = tok([p for k in keys for p in PROMPTS[k]]).cuda()
    with torch.no_grad():
        tf = model.encode_text(text)
        tf /= tf.norm(dim=-1, keepdim=True)
        ims = torch.stack([pre(f.convert("RGB")) for f in frames]).cuda()
        imf = model.encode_image(ims)
        imf /= imf.norm(dim=-1, keepdim=True)
        logits = (100.0 * imf @ tf.T).softmax(dim=-1).cpu().numpy()
    return {k: logits[:, i] for i, k in enumerate(keys)}


def pick(frames, model, pre, tok):
    s = scores(frames, model, pre, tok)
    back = int(np.argmax(s["back"]))
    before = np.arange(1, back)
    after = np.arange(back + 1, len(frames) - 1)
    right = int(before[np.argmax(s["side"][before])]) if len(before) else back
    left = int(after[np.argmax(s["side"][after])]) if len(after) else back
    return {"front": 0, "right": right, "back": back, "left": left}, s


if __name__ == "__main__":
    model, pre, tok = load()
    clips = {c: sorted(glob.glob(f"/home/nick/output/anim-still/clips/turn_{c}/*.png"))
             for c in ["aldric", "brann", "sera", "cavalier", "shopkeeper"]}
    fs = sorted(glob.glob("/home/nick/comfy/mess-with-comfy/output/anim_*.png"),
                key=lambda p: int(re.search(r"anim_(\d+)_", p).group(1)))
    rec = [x for x in fs if os.path.getmtime(x) > time.time() - 8 * 3600]
    clips["aldric1st"] = rec[374:396]
    from PIL import ImageDraw
    S, rows = 230, []
    out = {}
    for c, paths in clips.items():
        fr = [Image.open(x).convert("RGB") for x in paths]
        p, s = pick(fr, model, pre, tok)
        out[c] = p
        print(f"{c:11s} {p['front']},{p['right']},{p['back']},{p['left']}")
        print("   side ", " ".join(f"{v:.2f}" for v in s["side"]))
        print("   back ", " ".join(f"{v:.2f}" for v in s["back"]))
        row = Image.new("RGB", (S * 4, S + 26), (14, 14, 17))
        dr = ImageDraw.Draw(row)
        for k, d in enumerate(("front", "right", "back", "left")):
            row.paste(fr[p[d]].resize((S, S)), (k * S, 24))
            dr.text((k * S + 6, 6), f"{c} {d} f{p[d]}", fill=(180, 225, 255))
        rows.append(row)
    grid = Image.new("RGB", (rows[0].width, sum(r.height for r in rows)), (14, 14, 17))
    y = 0
    for r in rows:
        grid.paste(r, (0, y)); y += r.height
    grid.save("/home/nick/output/anim-still/facings/clip_picks.png")
    json.dump(out, open("/home/nick/output/anim-still/facings/clip_picks.json", "w"), indent=1)
    print("wrote grid")
