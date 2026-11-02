#!/usr/bin/env python3
"""analyze-process-behavior intro: dark countryside and a pyramid of light, nothing readable anywhere.
Foreground: a hedgerow in full silhouette across the lower edge, a field track running out of the bottom
right corner into darkness, dew pale grass heads along the track margin. Midground: open fields falling
gently to a low eastern horizon, a barn roof and a motionless vane at the extreme left as shape only, no
lit window anywhere. Background: the zodiacal pyramid rising tilted from the horizon through rain grey
into thunderhead violet, stars visible through its thinner upper reaches and standing out harder beyond
its edges, a narrow copper band of cloud across its foot. The glow holds steady, it does not flicker."""
import random, sys
from PIL import Image, ImageDraw, ImageFilter
random.seed(41)
A = sys.argv[1] if len(sys.argv) > 1 else ""
W, H = 1200, 520
VIOLET = (36, 27, 51); WHITE = (244, 246, 255); GREY = (154, 160, 168); COPPER = (184, 115, 51)
img = Image.new("RGB", (W, H), VIOLET); d = ImageDraw.Draw(img, "RGBA")
# sky: thunderhead violet overhead deepening, rain grey toward the eastern horizon at the right of centre
for y in range(0, 372):
    t = y / 372
    d.line([(0, y), (W, y)], fill=(int(30 + 26 * t), int(22 + 26 * t), int(46 + 22 * t)))
for x in range(W):  # eastern brightening low at the horizon
    t = max(0.0, 1 - abs(x - 760) / 620)
    d.line([(x, 300), (x, 372)], fill=(int(70 + 60 * t), int(66 + 52 * t), int(84 + 40 * t), 0))
# the zodiacal pyramid: tilted along the ecliptic, base at the horizon, tip leaning left as it climbs
base_l, base_r, hz = 560, 980, 372
apex = (706, 66) if A != "--v1" else (770, 66)  # v1 flaw: pyramid drawn upright, a tent silhouette
if A == "--v1":
    base_l, base_r, apex = 580, 960, (770, 66)
glow = Image.new("RGB", (W, H), (0, 0, 0)); gd = ImageDraw.Draw(glow)
for i, val in enumerate([52, 88, 128, 178]):
    inset = i * 30
    tipx = apex[0] + (770 - apex[0]) * i / 5
    gd.polygon([(base_l + inset, hz), (base_r - inset, hz), (tipx + 20 - i * 4, apex[1] + i * 30), (tipx - 20 + i * 4, apex[1] + i * 30)], fill=(val, val, val))
glow = glow.filter(ImageFilter.GaussianBlur(16))
img.paste(Image.new("RGB", (W, H), WHITE), (0, 0), glow.convert("L").point(lambda v: int(v * 0.62)))
d = ImageDraw.Draw(img, "RGBA")
# stars: fixed points, brighter and larger outside the triangle than inside it
def inside(x, y):
    if y > hz: return False
    t = (hz - y) / (hz - apex[1])
    cx = 770 + (apex[0] - 770) * t; half = (base_r - base_l) / 2 * (1 - t) + 14 * t
    return abs(x - cx) < half
for _ in range(300):
    x, y = random.uniform(0, W), random.uniform(4, 350)
    if inside(x, y):
        if A == "--v1":  # v1 flaw also equalises the stars, so the pyramid reads as painted glass
            r, a = random.uniform(1.0, 2.0), 235
        else:
            r, a = random.uniform(0.6, 1.2), 120  # stars show through the thin upper light, dimmer
    else:
        r, a = random.uniform(1.0, 2.1), 235  # outside the light the stars stand out harder
    d.ellipse([x - r, y - r, x + r, y + r], fill=(244, 246, 255, a))
# a narrow copper band of low cloud lying across the foot of the pyramid
band_h = 34 if A == "--v2" else 10  # v2 flaw: the band swells into a sunset stripe that owns the frame
for (x0, x1) in [(548, 742), (758, 906), (922, 996)]:
    d.rectangle([x0, hz - band_h, x1, hz + 3], fill=(COPPER[0], COPPER[1], COPPER[2], 190))
    d.rectangle([x0, hz - band_h, x1, hz - band_h + 3], fill=(214, 148, 92, 200))
# fields falling gently toward the horizon, near black violet
d.polygon([(0, hz), (W, hz), (W, H), (0, H)], fill=(22, 17, 33))
for yy, aa in [(398, 60), (430, 44), (466, 30)]:
    d.line([(0, yy), (W, yy - 8)], fill=(90, 84, 110, aa), width=2)
# barn roof and a motionless vane at the extreme left, shape only, no lit window
d.polygon([(0, 372), (0, 306), (58, 276), (128, 306), (128, 372)], fill=(10, 8, 16))
d.polygon([(0, 306), (58, 276), (128, 306), (128, 318), (0, 318)], fill=(14, 11, 22))
d.line([(58, 276), (58, 252)], fill=(10, 8, 16), width=3)
d.polygon([(58, 252), (86, 258), (58, 262)], fill=(10, 8, 16))  # the vane arrow, still, pointing east
d.line([(40, 258), (58, 258)], fill=(10, 8, 16), width=3)
# field track running out of the bottom right corner into darkness
d.polygon([(852, H), (986, 408), (1024, 408), (1064, H)], fill=(34, 28, 48))
d.polygon([(906, H), (1002, 408), (1012, 408), (984, H)], fill=(26, 21, 38))
# dew pale grass heads catching the faintest grey along the track margin
for _ in range(46):
    t = random.random(); x = 852 + t * 190 + random.uniform(-16, 30); y = H - t * (H - 412) + random.uniform(-4, 4)
    ln = random.uniform(6, 14)
    d.line([(x, y), (x + random.uniform(-2, 2), y - ln)], fill=(196, 200, 208, 120), width=1)
    d.ellipse([x - 1.6, y - ln - 1.6, x + 1.6, y - ln + 1.6], fill=(216, 220, 228, 140))
# hedgerow in full silhouette across the lower edge
if A != "--v2":  # v2 also drops the hedgerow, leaving the bottom edge as bare field
    for x in range(-20, W + 20, 26):
        top = 486 + random.uniform(-10, 8)
        d.ellipse([x - 30, top - 26, x + 30, 540], fill=(8, 6, 13))
    d.rectangle([0, 500, W, H], fill=(8, 6, 13))
img = img.filter(ImageFilter.GaussianBlur(0.5))
out = {"--v1": "scratch/intro-v1.png", "--v2": "scratch/intro-v2.png"}.get(A, "intro-banner.png")
img.save(__file__.rsplit("/", 1)[0] + "/" + out); print("saved", out)
