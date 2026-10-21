"""Generate the 512x512 Shrek player atlas.

The atlas is intentionally flat-shaded and low-colour, in the spirit of a
2003 GoldSrc player skin.  Large areas are single flat colours: the final
texture is quantised to a 256-entry indexed BMP, and smooth gradients in the
source turn into visible bands after quantisation.  Detail is painted with
deliberate high-contrast marks (stitching, seams, dirt) instead.

Every patch is periodic in U so tube UVs wrap without a visible seam.
"""
from __future__ import annotations

import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = r"C:\AI\goldsrc\shrek_player"
TEX_DIR = os.path.join(ROOT, "textures")
PNG_PATH = os.path.join(TEX_DIR, "shrek_atlas.png")
BMP_PATH = os.path.join(TEX_DIR, "shrek.bmp")

W = H = 512

# name -> (x, y, w, h) in top-left image pixels
PATCHES = {
    "skin": (0, 0, 128, 128),
    "tunic": (128, 0, 128, 128),
    "vest": (256, 0, 128, 128),
    "pants": (384, 0, 128, 128),
    "shoe": (0, 128, 128, 128),
    "sole": (128, 128, 128, 128),
    "belt": (256, 128, 128, 128),
    "ear_inner": (384, 128, 128, 128),
    "nose": (0, 256, 128, 128),
    "eye_white": (128, 256, 64, 64),
    "iris": (192, 256, 64, 64),
    "pupil": (256, 256, 64, 64),
    "brow": (320, 256, 64, 64),
    "mouth": (384, 256, 64, 64),
    "teeth": (448, 256, 64, 64),
    "tongue": (0, 384, 64, 64),
    "buckle": (64, 384, 64, 64),
    "cheek": (128, 384, 64, 64),
    "dark": (192, 384, 64, 64),
    "highlight": (256, 384, 64, 64),
    "unused": (320, 384, 64, 64),
}

# Flat base colours.  Shrek's ogre green is deliberately yellow-green, the
# tunic a warm unbleached linen, and the leather a swampy mid brown.
BASE = {
    "skin": (122, 164, 74),
    "tunic": (210, 194, 157),
    "vest": (94, 61, 37),
    "pants": (103, 79, 53),
    "shoe": (80, 55, 34),
    "sole": (43, 31, 21),
    "belt": (72, 49, 29),
    "ear_inner": (72, 96, 43),
    "nose": (122, 164, 74),
    "eye_white": (244, 240, 227),
    "iris": (113, 78, 38),
    "pupil": (14, 10, 8),
    "brow": (66, 42, 22),
    "mouth": (72, 28, 24),
    "teeth": (236, 227, 201),
    "tongue": (170, 96, 90),
    "buckle": (184, 146, 70),
    "cheek": (118, 158, 72),
    "dark": (27, 20, 14),
    "highlight": (223, 232, 202),
    "unused": (64, 64, 64),
}


def _paint(name: str, rgb: np.ndarray) -> None:
    x, y, w, h = PATCHES[name]
    rgb[y:y + h, x:x + w] = BASE[name]


def _draw_details(img: Image.Image) -> None:
    draw = ImageDraw.Draw(img)

    # Tunic: a few long, soft fold creases.  They run vertically in the
    # atlas, i.e. around the torso, and repeat cleanly at the UV seam.
    x0, y0, w, h = PATCHES["tunic"]
    for fx, shade in ((0.18, (196, 178, 140)), (0.47, (201, 184, 147)),
                      (0.74, (198, 181, 144))):
        x = x0 + int(fx * w)
        draw.line([(x, y0 + 6), (x + 2, y0 + h - 6)], fill=shade, width=2)
        draw.line([(x + 1, y0 + 8), (x + 3, y0 + h - 8)],
                  fill=(219, 204, 170), width=1)

    # Vest: stitch dashes along the two open front edges, plus a centre-back
    # seam.  The open strip's u=0 and u=1 are the front edges; u=0.5 is the
    # middle of the back.
    x0, y0, w, h = PATCHES["vest"]
    for edge_x in (x0 + 2, x0 + w - 4):
        for y in range(y0 + 4, y0 + h - 6, 8):
            draw.rectangle([edge_x, y, edge_x + 1, y + 4],
                           fill=(143, 106, 68))
    sx = x0 + w // 2
    draw.line([(sx, y0 + 4), (sx, y0 + h - 4)], fill=(78, 50, 30), width=2)
    draw.line([(sx + 2, y0 + 6), (sx + 2, y0 + h - 6)],
              fill=(122, 88, 56), width=1)

    # Belt: two rows of tan stitching.
    x0, y0, w, h = PATCHES["belt"]
    for yy in (y0 + 22, y0 + h - 24):
        for x in range(x0 + 2, x0 + w - 2, 8):
            draw.line([(x, yy), (x + 3, yy)], fill=(160, 128, 80), width=2)

    # Pants stay flat: the same patch is used by thigh and calf tubes, and
    # any painted band would repeat at both ends of each tube.

    # Shoes: a slightly worn lighter toe band at the front of each tube
    # (the toe end of the tube maps to v=1, the top of the patch).
    x0, y0, w, h = PATCHES["shoe"]
    draw.rectangle([x0, y0, x0 + w - 1, y0 + 9], fill=(95, 67, 42))

    # Teeth: three thin dark grooves so the white strip reads as separate
    # teeth rather than a moustache.  The tube's v runs along the tooth row.
    x0, y0, w, h = PATCHES["teeth"]
    for fy in (0.22, 0.52, 0.78):
        yy = y0 + int(fy * h)
        draw.line([(x0, yy), (x0 + w - 1, yy)], fill=(96, 82, 68), width=2)


def make_atlas() -> Image.Image:
    os.makedirs(TEX_DIR, exist_ok=True)
    rgb = np.zeros((H, W, 3), dtype=np.uint8)
    rgb[:] = (36, 36, 36)
    for name in PATCHES:
        _paint(name, rgb)
    img = Image.fromarray(rgb, "RGB")
    _draw_details(img)
    return img


def main() -> None:
    img = make_atlas()
    img.save(PNG_PATH)
    print("wrote", PNG_PATH, img.size)
    # Quantised BMP is produced by the toolchain converter (proper 256-entry
    # palette).  Flat colour fields survive quantisation without banding.
    if "--bmp" in sys.argv:
        from bl_ext.user_default.goldsrc_model_toolchain.core.textures import convert_to_indexed_bmp
        facts = convert_to_indexed_bmp(PNG_PATH, BMP_PATH, width=W, height=H,
                                       modes=(), require_masked_pixels=False)
        print("wrote", BMP_PATH, facts.get("used_color_count"))


if __name__ == "__main__":
    main()
