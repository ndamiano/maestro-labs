"""A turntable for each character, then the two pickers on each — no judgement, just picks."""
import subprocess, sys, glob, os, json
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/nick/Documents/ai-agent-test/src")
sys.path.insert(0, "/home/nick/Documents/Labs/anim-still")
from tools.comfyui_tools import _I2V_TURN, _I2V_TURN_LENGTH, _I2V_TURN_STEPS  # noqa
from worker import anim_sheet as sheets  # noqa
import pick_facings2  # noqa

CHARS = ["aldric", "brann", "sera", "cavalier", "shopkeeper"]
SRC = "/home/nick/output/anim-still/{c}_front_s1000.png"
OUT = Path("/home/nick/output/anim-still/turntables")
OUT.mkdir(parents=True, exist_ok=True)

rows = []
for c in CHARS:
    label = f"turn_{c}"
    d = Path("/home/nick/output/anim-still/clips") / label
    if not d.exists():
        subprocess.run([
            "/home/nick/Documents/ai-agent-test/venv/bin/python",
            "/home/nick/Documents/Labs/anim-still/one_clip.py",
            "--still", SRC.format(c=c), "--action", _I2V_TURN, "--facing", "",
            "--pin", "off", "--length", str(_I2V_TURN_LENGTH),
            "--steps", str(_I2V_TURN_STEPS), "--label", label], check=True)
    frames = [Image.open(p).convert("RGB") for p in sorted(glob.glob(str(d / "*.png")))]
    new, mirror = pick_facings2.pick(frames)
    old = sheets.pick_facings(frames)
    rows.append({"char": c, "old": old, "new": new, "mirror": round(mirror, 4)})
    print(c, "old", old, "new", new, f"mirror {mirror:.4f}", flush=True)
    for name, p in (("old", old), ("new", new)):
        sheet = Image.new("RGB", (256 * 4, 288), (18, 18, 22))
        dr = ImageDraw.Draw(sheet)
        for k, dd in enumerate(("front", "right", "back", "left")):
            sheet.paste(frames[p[dd]].resize((256, 256)), (256 * k, 32))
            dr.text((256 * k + 8, 10), f"{dd}   frame {p[dd]}", fill=(232, 232, 238))
        sheet.save(OUT / f"{c}_{name}.png")
    # both pickers stacked, for one glance per character
    a = Image.open(OUT / f"{c}_old.png"); b = Image.open(OUT / f"{c}_new.png")
    both = Image.new("RGB", (a.width, a.height * 2 + 24), (10, 10, 12))
    dr = ImageDraw.Draw(both)
    both.paste(a, (0, 0)); both.paste(b, (0, a.height + 24))
    dr.text((8, a.height + 6), "NEW (asymmetry)", fill=(150, 230, 150))
    dr.text((8, 2), "", fill=(255, 255, 255))
    both.save(OUT / f"{c}_compare.png")
(OUT / "picks.json").write_text(json.dumps(rows, indent=1))
print("done")
