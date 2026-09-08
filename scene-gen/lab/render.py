"""Flat-color PNG rendering of tile grids plus per-place contact sheets."""
import re

from PIL import Image, ImageDraw, ImageFont

TILE = 20
FALLBACK_PALETTE = [
    "#4caf50", "#2196f3", "#9e9e9e", "#795548", "#ffeb3b",
    "#e91e63", "#00bcd4", "#8bc34a", "#ff9800", "#607d8b",
    "#673ab7", "#c62828", "#33691e", "#f5f5dc", "#37474f",
]


def parse_color(c, index):
    if isinstance(c, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", c.strip()):
        return c.strip()
    return FALLBACK_PALETTE[index % len(FALLBACK_PALETTE)]


def render_map(grid, terrain_colors, placements, object_colors, out_path):
    """grid: list of strings (terrain only). placements: [{'symbol','row','col'}]."""
    h, w = len(grid), len(grid[0])
    img = Image.new("RGB", (w * TILE, h * TILE), "#000000")
    draw = ImageDraw.Draw(img)
    for r in range(h):
        for c in range(w):
            color = terrain_colors.get(grid[r][c], "#ff00ff")
            draw.rectangle([c * TILE, r * TILE, (c + 1) * TILE - 1, (r + 1) * TILE - 1], fill=color)
    font = ImageFont.load_default()
    for p in placements:
        r, c, sym = p["row"], p["col"], p["symbol"]
        color = object_colors.get(sym, "#ffffff")
        pad = 3
        draw.rectangle([c * TILE + pad, r * TILE + pad,
                        (c + 1) * TILE - 1 - pad, (r + 1) * TILE - 1 - pad],
                       fill=color, outline="#000000")
        draw.text((c * TILE + 6, r * TILE + 4), sym, fill="#000000", font=font)
    img.save(out_path)
    return img


def contact_sheet(image_paths, labels, out_path, title=""):
    imgs = [Image.open(p) for p in image_paths]
    pad, header, footer = 10, 24, 18
    wmax = max(i.width for i in imgs)
    hmax = max(i.height for i in imgs)
    sheet = Image.new("RGB", (pad + len(imgs) * (wmax + pad), header + hmax + footer), "#222222")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    draw.text((pad, 5), title, fill="#ffffff", font=font)
    for i, (img, label) in enumerate(zip(imgs, labels)):
        x = pad + i * (wmax + pad)
        sheet.paste(img, (x, header))
        draw.text((x, header + hmax + 2), label, fill="#ffffff", font=font)
    sheet.save(out_path)
