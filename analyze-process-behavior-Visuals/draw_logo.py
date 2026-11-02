#!/usr/bin/env python3
"""analyze-process-behavior logo: a tall triangle of pale light leaning along the ecliptic, point up and
base wide at a low dark horizon, one clean pyramid of glow in lightning white softening at its edges into
rain grey. A thin copper line marks the horizon, small fixed stars show through the fainter upper half,
brighter outside the triangle than inside it. The ground under the horizon stays thunderhead violet,
almost black, no building, tree, or figure. Beneath the horizon the name is set in B612 Mono in lightning
white on thunderhead violet, letters spaced evenly like readings taken at fixed intervals."""
import random, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
random.seed(7)
A = sys.argv[1] if len(sys.argv) > 1 else ""
W, H = 900, 520
VIOLET = (36, 27, 51); WHITE = (244, 246, 255); GREY = (154, 160, 168); COPPER = (184, 115, 51)
img = Image.new("RGB", (W, H), VIOLET); d = ImageDraw.Draw(img, "RGBA")
HZ = 356
for y in range(0, HZ):
    t = y / HZ
    d.line([(0, y), (W, y)], fill=(int(30 + 20 * t), int(22 + 20 * t), int(46 + 18 * t)))
base_l, base_r = 240, 660
apex = (392, 52) if A != "--v1" else (450, 52)  # v1 flaw: apex centred, a warning sign triangle
glow = Image.new("RGB", (W, H), (0, 0, 0)); gd = ImageDraw.Draw(glow)
for i, val in enumerate([58, 96, 140, 190]):
    inset = i * 28
    tipx = apex[0] + (450 - apex[0]) * i / 5
    gd.polygon([(base_l + inset, HZ), (base_r - inset, HZ), (tipx + 17 - i * 4, apex[1] + i * 28), (tipx - 17 + i * 4, apex[1] + i * 28)], fill=(val, val, val))
glow = glow.filter(ImageFilter.GaussianBlur(13))
img.paste(Image.new("RGB", (W, H), WHITE), (0, 0), glow.convert("L").point(lambda v: int(v * 0.66)))
d = ImageDraw.Draw(img, "RGBA")
def inside(x, y):
    if y > HZ: return False
    t = (HZ - y) / (HZ - apex[1]); cx = 450 + (apex[0] - 450) * t; half = 210 * (1 - t) + 12 * t
    return abs(x - cx) < half
for _ in range(190):
    x, y = random.uniform(0, W), random.uniform(4, HZ - 6)
    if inside(x, y) and y < 210:
        r, a = random.uniform(0.6, 1.1), 115
    elif inside(x, y):
        continue
    else:
        r, a = random.uniform(1.0, 1.9), 235
    d.ellipse([x - r, y - r, x + r, y + r], fill=(244, 246, 255, a))
# ground under the horizon: thunderhead violet, almost black, empty
d.rectangle([0, HZ, W, H], fill=(20, 15, 30))
d.line([(0, HZ), (W, HZ)], fill=COPPER, width=3)  # the thin copper horizon line
try:
    fm = ImageFont.truetype(__file__.rsplit("/", 1)[0] + "/fonts/B612Mono.ttf", 27)
    fc = ImageFont.truetype(__file__.rsplit("/", 1)[0] + "/fonts/Cabin.ttf", 30)
except Exception:
    fm = fc = ImageFont.load_default()
name = "analyze-process-behavior"
if A == "--v2":  # v2 flaw: the name set as running text in the reading face, no fixed interval spacing
    d.text((450, 438), name, font=fc, fill=WHITE, anchor="mm")
else:
    cell = 33; total = cell * len(name); x = 450 - total / 2
    for c in name:
        d.text((x + cell / 2, 438), c, font=fm, fill=WHITE, anchor="mm"); x += cell
img = img.filter(ImageFilter.GaussianBlur(0.3))
out = {"--v1": "scratch/logo-v1.png", "--v2": "scratch/logo-v2.png"}.get(A, "logo.png")
img.save(__file__.rsplit("/", 1)[0] + "/" + out)
if A == "":
    img.resize((64, 37)).save(__file__.rsplit("/", 1)[0] + "/scratch/logo64-ship.png")
print("saved", out)
