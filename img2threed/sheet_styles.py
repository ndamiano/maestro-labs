"""Render every style-grid GLB and lay out one sheet per subject: rows = styles, columns =
input | TRELLIS 512 (3 views) | TRELLIS 1024 (3 views)."""
import os, subprocess, sys
from PIL import Image, ImageDraw

O = "/home/nick/output/img2threed"
PY = "/home/nick/Documents/ai-agent-test/venv/bin/python"
HERE = os.path.dirname(os.path.abspath(__file__))
SUBS = ["wooden-watchtower", "rustic-stone-cottage", "weathered-wooden-barrel", "broken-wooden-cart", "gnarled-old-oak-tree"]
STY = ["A-photo", "B-lowpoly", "C-handpainted", "D-cgrender", "E-product"]

for n in SUBS:
    rows = []
    for t in STY:
        tiles = []
        src = Image.open(f"{O}/styles/{n}.{t}.png").convert("RGBA").resize((512, 512))
        bg = Image.new("RGBA", (512, 512), (200, 200, 200, 255)); bg.alpha_composite(src)
        tiles.append(bg.convert("RGB"))
        for tier in ("512", "1024"):
            glb = f"{O}/styles_{tier}/{n}.{t}.glb"
            png = f"{O}/styles_{tier}/{n}.{t}.render.png"
            if not os.path.exists(png):
                if not os.path.exists(glb) or os.path.getsize(glb) == 0:
                    tiles.append(Image.new("RGB", (1536, 512), "pink")); continue
                subprocess.run([PY, f"{HERE}/render_glb.py", png, glb], check=True, capture_output=True)
            tiles.append(Image.open(png).convert("RGB"))
        row = Image.new("RGB", (512 + 1536 * 2, 512), "white")
        x = 0
        for im in tiles:
            row.paste(im, (x, 0)); x += im.width
        ImageDraw.Draw(row).text((6, 6), t, fill="red")
        rows.append(row)
    sheet = Image.new("RGB", (rows[0].width, 512 * len(rows)), "white")
    for i, r in enumerate(rows):
        sheet.paste(r, (0, 512 * i))
    sheet.resize((sheet.width // 2, sheet.height // 2)).save(f"{O}/sheet_styles_{n}.png")
    print(n, flush=True)
