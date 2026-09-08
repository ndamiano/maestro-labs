"""Contact sheet: one row per asset id, one column per arm (prod first). Also prints per-arm stats:
frame-touch count (subject clipped by the 1024 frame), mean semi-alpha fraction, magenta-key loss.

usage: python sheet.py <arm> [<arm> ...]   -> sheets/<arms>.png
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).parent
import os
PROMPTS = json.load(open(HERE / os.environ.get("PROMPTS", "prompts.json")))
CELL = 220


def checker(size):
    bg = Image.new("RGBA", size, (0, 0, 0, 0))
    for y in range(0, size[1], 16):
        for x in range(0, size[0], 16):
            bg.paste((200, 200, 200, 255) if (x // 16 + y // 16) % 2 else (120, 120, 120, 255), (x, y, min(x + 16, size[0]), min(y + 16, size[1])))
    return bg


def stats(im):
    a = im.split()[-1]
    bb = a.getbbox() or (0, 0, 0, 0)
    touch = int(bb[0] <= 0) + int(bb[1] <= 0) + int(bb[2] >= im.width) + int(bb[3] >= im.height)
    h = a.histogram()
    semi = sum(h[1:255]) / (im.width * im.height)
    mag = tot = 0
    for r, g, b, al in im.getdata():
        if al > 128:
            tot += 1
            if r > 135 and b > 105 and g < r - 35 and g < b - 25:
                mag += 1
    return touch, semi, (mag / tot if tot else 0)


def load(arm, aid):
    if arm == "prod":
        p = HERE / os.environ.get("PROD", "prod_assets") / f"{aid}.webp"
    else:
        p = HERE / os.environ.get("ARMS", "arms") / arm / f"{aid}.png"
    return Image.open(p).convert("RGBA") if p.exists() else None


def main():
    args = sys.argv[1:]
    sel = PROMPTS
    if "--rows" in args:
        i = args.index("--rows"); a, b = map(int, args[i + 1].split(":")); sel = PROMPTS[a:b]; del args[i:i + 2]
    arms = ["prod"] + args
    rows = len(sel)
    sheet = Image.new("RGB", (len(arms) * CELL + 120, rows * CELL + 30), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    agg = {a: [0, 0.0, 0.0, 0] for a in arms}
    for j, a in enumerate(arms):
        d.text((120 + j * CELL + 4, 8), a, fill=(255, 255, 0))
    for i, p in enumerate(sel):
        d.text((4, 30 + i * CELL + CELL // 2), p["id"], fill=(255, 255, 255))
        for j, a in enumerate(arms):
            im = load(a, p["id"])
            if im is None:
                continue
            t, s, m = stats(im)
            agg[a][0] += t; agg[a][1] += s; agg[a][2] += m; agg[a][3] += 1
            th = im.copy(); th.thumbnail((CELL - 8, CELL - 24))
            bg = checker(th.size); bg.alpha_composite(th)
            x, y = 120 + j * CELL + 4, 30 + i * CELL + 2
            sheet.paste(bg.convert("RGB"), (x, y))
            d.text((x, y + CELL - 20), f"touch{t} semi{s:.2f} mag{m*100:.0f}%", fill=(255, 200, 200) if (t or m > 0.02) else (180, 255, 180))
    out = HERE / "sheets"; out.mkdir(exist_ok=True)
    name = out / ("_".join(arms) + f"_{sel[0]['id']}.png")
    sheet.save(name)
    print(name)
    for a, (t, s, m, n) in agg.items():
        if n:
            print(f"{a:10} n={n:2}  frame-touch edges={t:2}  mean semi-alpha={s/n:.3f}  mean magenta-loss={m/n*100:.1f}%")


if __name__ == "__main__":
    main()
