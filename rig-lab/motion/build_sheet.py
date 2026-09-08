import os
from PIL import Image, ImageDraw, ImageFont

POSES = ["idle", "walk_a", "walk_b", "attack_windup", "attack_strike",
         "block", "hit", "cast", "jump", "death"]
RIGS = ["knight", "troll", "specter"]
VIEWS = ["front", "iso"]

CELL = 220
LABEL_H = 22
ROW_LABEL_W = 130
HEADER_H = 40
DIR = "motion/poses"

cols = [(r, v) for r in RIGS for v in VIEWS]
W = ROW_LABEL_W + CELL * len(cols)
H = HEADER_H + (CELL + LABEL_H) * len(POSES)

sheet = Image.new("RGB", (W, H), (255, 255, 255))
draw = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
except Exception:
    font = ImageFont.load_default()
    font_s = font

for ci, (rig, view) in enumerate(cols):
    x = ROW_LABEL_W + ci * CELL
    draw.text((x + 8, 10), f"{rig}/{view}", fill=(0, 0, 0), font=font)

for ri, pose in enumerate(POSES):
    y = HEADER_H + ri * (CELL + LABEL_H)
    draw.text((6, y + CELL // 2 - 8), pose, fill=(0, 0, 0), font=font)
    for ci, (rig, view) in enumerate(cols):
        x = ROW_LABEL_W + ci * CELL
        path = os.path.join(DIR, f"{rig}_{pose}_{view}.png")
        if os.path.exists(path):
            im = Image.open(path).convert("RGBA")
            bg = Image.new("RGBA", im.size, (245, 245, 245, 255))
            bg.alpha_composite(im)
            bg = bg.convert("RGB").resize((CELL, CELL))
            sheet.paste(bg, (x, y))
        else:
            draw.rectangle([x, y, x + CELL, y + CELL], outline=(255, 0, 0))
        draw.text((x + 2, y + CELL + 2), f"{rig}_{pose}", fill=(90, 90, 90), font=font_s)

sheet.save("motion/poses/sheet.png")
print("saved motion/poses/sheet.png", sheet.size)
