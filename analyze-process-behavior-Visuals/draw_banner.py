#!/usr/bin/env python3
"""analyze-process-behavior wordmark banner: true dark countryside in the last hour before sunrise, shot
from a field track with no house light, road lamp, or town glow. A broad pyramid of faint white light
climbs from the horizon at an angle, following the tilt of the ecliptic, its base hidden behind a copper
lit band of low cloud and its tip dissolving among stars. The sky deepens to thunderhead violet overhead
and rain grey at the western edge, where a few stars still hold at full strength. A hedgerow runs black
across the bottom, and a weather vane on a barn roof at the far left stands in profile, still, its arrow
pointing into the wind that has not yet arrived. The project name is painted in B612 Mono in faded
lightning white on the barn gable, small, on violet shadowed timber, and it is the only writing."""
import random, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
random.seed(23)
A = sys.argv[1] if len(sys.argv) > 1 else ""
W, H = 1200, 420
VIOLET = (36, 27, 51); WHITE = (244, 246, 255); COPPER = (184, 115, 51)
img = Image.new("RGB", (W, H), VIOLET); d = ImageDraw.Draw(img, "RGBA")
HZ = 316
for y in range(0, HZ):
    t = y / HZ
    d.line([(0, y), (W, y)], fill=(int(32 + 22 * t), int(24 + 22 * t), int(48 + 20 * t)))
for x in range(0, 340):  # rain grey at the western edge
    a = int(46 * (1 - x / 340))
    d.line([(x, 0), (x, HZ)], fill=(154, 160, 168, a))
base_l, base_r, apex = 520, 1020, (692, 44)
glow = Image.new("RGB", (W, H), (0, 0, 0)); gd = ImageDraw.Draw(glow)
for i, val in enumerate([48, 84, 124, 172]):
    inset = i * 30
    tipx = apex[0] + (770 - apex[0]) * i / 5
    gd.polygon([(base_l + inset, HZ), (base_r - inset, HZ), (tipx + 19 - i * 4, apex[1] + i * 28), (tipx - 19 + i * 4, apex[1] + i * 28)], fill=(val, val, val))
glow = glow.filter(ImageFilter.GaussianBlur(15))
img.paste(Image.new("RGB", (W, H), WHITE), (0, 0), glow.convert("L").point(lambda v: int(v * 0.6)))
d = ImageDraw.Draw(img, "RGBA")
def inside(x, y):
    if y > HZ: return False
    t = (HZ - y) / (HZ - apex[1]); cx = 770 + (apex[0] - 770) * t; half = 250 * (1 - t) + 14 * t
    return abs(x - cx) < half
for _ in range(280):
    x, y = random.uniform(0, W), random.uniform(4, 300)
    if inside(x, y):
        r, a = random.uniform(0.6, 1.1), 110
    else:
        r, a = random.uniform(1.0, 2.0), 235  # western stars hold at full strength
    d.ellipse([x - r, y - r, x + r, y + r], fill=(244, 246, 255, a))
for (x0, x1) in [(508, 724), (740, 892), (908, 1032)]:  # copper lit band of low cloud across the base only
    d.rectangle([x0, HZ - 10, x1, HZ + 2], fill=(184, 115, 51, 190))
    d.rectangle([x0, HZ - 10, x1, HZ - 7], fill=(214, 148, 92, 200))
d.polygon([(0, HZ), (W, HZ), (W, H), (0, H)], fill=(20, 15, 30))  # dark fields
# barn at the far left: roof, gable of violet shadowed timber, and the still vane in profile
d.polygon([(18, HZ + 6), (18, 236), (92, 198), (176, 236), (176, HZ + 6)], fill=(13, 10, 20))
d.polygon([(8, 240), (92, 194), (186, 240), (186, 252), (8, 252)], fill=(17, 13, 26))
for x in range(34, 168, 22):  # timber boards on the gable
    d.line([(x, 246), (x, HZ)], fill=(30, 24, 44), width=3)
d.line([(92, 194), (92, 168)], fill=(13, 10, 20), width=3)
d.polygon([(92, 168), (122, 174), (92, 178)], fill=(13, 10, 20))  # vane arrow pointing into the wind
d.line([(72, 174), (92, 174)], fill=(13, 10, 20), width=3)
try:
    f = ImageFont.truetype(__file__.rsplit("/", 1)[0] + "/fonts/B612Mono.ttf", 15)
    fbig = ImageFont.truetype(__file__.rsplit("/", 1)[0] + "/fonts/B612Mono.ttf", 44)
except Exception:
    f = fbig = ImageFont.load_default()
name = "analyze-process-behavior"
if A == "--v1":  # v1 flaw: the name lettered on a board planted in the field, signage the scene does not have
    d.rectangle([760, 238, 1130, 282], fill=(17, 13, 26), outline=(120, 110, 130), width=2)
    d.rectangle([930, 282, 944, HZ + 20], fill=(13, 10, 20))
    d.text((945, 260), name, font=f, fill=(226, 229, 240), anchor="mm")
elif A == "--v2":  # v2 flaw: the name huge and crisp across the sky, louder than the light itself
    d.text((600, 120), name, font=fbig, fill=(250, 250, 255))
else:
    # painted on the gable in faded lightning white, small enough that a passerby must stop to read it
    for i, line in enumerate(["analyze-", "process-", "behavior"]):
        d.text((30, 258 + i * 17), line, font=f, fill=(196, 199, 214, 205))
    for _ in range(14):  # weather fading on the paint
        x, y = random.uniform(30, 150), random.uniform(256, 306)
        d.line([(x, y), (x + random.uniform(4, 12), y)], fill=(24, 19, 36), width=1)
# hedgerow black across the bottom of the frame
for x in range(-20, W + 20, 26):
    top = 384 + random.uniform(-9, 7)
    d.ellipse([x - 30, top - 24, x + 30, 440], fill=(7, 5, 12))
d.rectangle([0, 398, W, H], fill=(7, 5, 12))
img = img.filter(ImageFilter.GaussianBlur(0.5))
out = {"--v1": "scratch/banner-v1.png", "--v2": "scratch/banner-v2.png"}.get(A, "banner.png")
img.save(__file__.rsplit("/", 1)[0] + "/" + out); print("saved", out)
