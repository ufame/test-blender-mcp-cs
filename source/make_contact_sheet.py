"""Build a labelled contact sheet for the delivered Shrek player model."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"C:\AI\goldsrc\shrek_player")
OUT = ROOT / "renders" / "final_contact_sheet.png"

TILES = [
    ("idle1", "idle1 - Blender preview", ROOT / "renders" / "final_blend_idle.png"),
    ("walk", "walk - Blender preview", ROOT / "renders" / "pose_walk.png"),
    ("run", "run - Blender preview", ROOT / "renders" / "pose_run.png"),
    ("crouch", "crouch_idle - Blender preview", ROOT / "renders" / "pose_crouch.png"),
    ("jump", "jump - Blender preview", ROOT / "renders" / "pose_jump.png"),
    ("shoot", "rifle shoot blend - Blender preview", ROOT / "renders" / "pose_shoot.png"),
    ("reload", "rifle reload - Blender preview", ROOT / "renders" / "pose_reload.png"),
    ("death", "death1 - Blender preview", ROOT / "renders" / "pose_death.png"),
    ("csfront", "CS 1.6 GoldClient - front", ROOT / "renders" / "cs_ingame_front_crop.png"),
    ("csside", "CS 1.6 GoldClient - side", ROOT / "renders" / "cs_ingame_side_crop.png"),
    ("csback", "CS 1.6 GoldClient - back", ROOT / "renders" / "cs_ingame_back_crop.png"),
    ("atlas", "diffuse atlas - 512 x 512 indexed BMP", ROOT / "textures" / "shrek_atlas.png"),
]

COLS = 4
CELL_W = 440
CELL_H = 500
PAD = 18
HEADER = 100
FOOTER = 50
BG = (23, 26, 31)
CARD = (32, 36, 42)
WHITE = (238, 240, 243)
MUTED = (160, 168, 178)
ACCENT = (126, 201, 80)

font_path = r"C:\Windows\Fonts\segoeui.ttf"
bold_path = r"C:\Windows\Fonts\segoeuib.ttf"
try:
    title_font = ImageFont.truetype(bold_path, 38)
    label_font = ImageFont.truetype(font_path, 19)
    foot_font = ImageFont.truetype(font_path, 18)
except OSError:
    title_font = ImageFont.load_default()
    label_font = ImageFont.load_default()
    foot_font = ImageFont.load_default()

width = COLS * CELL_W
height = HEADER + 3 * CELL_H + FOOTER
sheet = Image.new("RGB", (width, height), BG)
draw = ImageDraw.Draw(sheet)

draw.text((PAD, 22), "SHREK PLAYER", font=title_font, fill=ACCENT)
draw.text((PAD + 290, 32), "CS 1.6 / GoldSrc player model", font=label_font, fill=WHITE)
draw.text((PAD + 290, 58), "55 bones - 111 sequences - 3257 triangles - MDL v10", font=label_font, fill=MUTED)

for index, (key, label, path) in enumerate(TILES):
    col = index % COLS
    row = index // COLS
    x = col * CELL_W
    y = HEADER + row * CELL_H
    draw.rounded_rectangle((x + 8, y + 8, x + CELL_W - 8, y + CELL_H - 8), radius=12, fill=CARD)

    image = Image.open(path).convert("RGB")
    box_w = CELL_W - 40
    box_h = 400
    scale = min(box_w / image.width, box_h / image.height)
    resized = image.resize((max(1, round(image.width * scale)), max(1, round(image.height * scale))), Image.LANCZOS)
    px = x + (CELL_W - resized.width) // 2
    py = y + 18 + (box_h - resized.height) // 2
    sheet.paste(resized, (px, py))

    draw.text((x + 22, y + 438), label, font=label_font, fill=WHITE)

draw.text(
    (PAD, height - 36),
    "Base skeleton and 111 sequences: decompiled CS 1.6 arctic.mdl. Rigid 1.0 weights, 55 bones preserved.",
    font=foot_font,
    fill=MUTED,
)
draw.text(
    (width - 300, height - 36),
    "C:\\AI\\goldsrc\\shrek_player",
    font=foot_font,
    fill=MUTED,
)

sheet.save(OUT, optimize=True)
print("WROTE", OUT, sheet.size)
