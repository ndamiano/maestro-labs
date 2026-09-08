"""What the player actually sees: each arm's sprites drawn at the game's own w,h (data.js) with
imageSmoothing off (NEAREST), then magnified 4x. One row per arm.

usage: python ingame.py <arm> [<arm> ...] -> sheets/ingame_<arms>.png
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).parent
SIZES = {"hero": (36, 44), "goblin": (40, 44), "wolf": (54, 40), "skeleton": (40, 54), "orc": (48, 56),
         "troll": (58, 66), "dark_knight": (46, 58), "wyvern": (66, 48), "dragon": (80, 66),
         "lich": (46, 60), "demon_lord": (74, 82), "potion_icon": (26, 26), "coin_icon": (24, 24)}
MAG = 4


def load(arm, aid):
    p = HERE / "prod_assets" / f"{aid}.webp" if arm == "prod" else HERE / "arms" / arm / f"{aid}.png"
    return Image.open(p).convert("RGBA") if p.exists() else None


def main():
    arms = ["prod"] + sys.argv[1:]
    cell_w = 90 * MAG; cell_h = 84 * MAG + 10
    sheet = Image.new("RGB", (len(SIZES) * cell_w + 100, len(arms) * cell_h), (28, 24, 44))
    d = ImageDraw.Draw(sheet)
    for r, arm in enumerate(arms):
        d.text((4, r * cell_h + cell_h // 2), arm, fill=(255, 255, 0))
        for c, (aid, (w, h)) in enumerate(SIZES.items()):
            im = load(arm, aid)
            if im is None:
                continue
            small = im.resize((w, h), Image.NEAREST).resize((w * MAG, h * MAG), Image.NEAREST)
            x = 100 + c * cell_w + (cell_w - small.width) // 2
            y = r * cell_h + cell_h - small.height - 5
            sheet.alpha_composite(small, (x, y)) if sheet.mode == "RGBA" else sheet.paste(small, (x, y), small)
    out = HERE / "sheets" / ("ingame_" + "_".join(arms) + ".png")
    sheet.save(out); print(out)


if __name__ == "__main__":
    main()
