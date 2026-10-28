"""Instagram profile picture of the presenter: 1080x1080, face centred for the circular crop.
Usage: python3 tools/make_profile.py assets/presenter out.png [circle_preview.png]"""
import sys
import numpy as np
from PIL import Image, ImageDraw
D = sys.argv[1]
ch = Image.new("RGBA", (1080, 920), (0, 0, 0, 0))
for n in ("body", "head", "eyes_open", "brows_neutral", "mouth_rest", "mustache"):
    ch.alpha_composite(Image.open(f"{D}/{n}.png"))
grid = ch.resize((108, 92), Image.NEAREST)               # back to the 1-pixel art grid
P, Z = 1080, 13
# background: brand blue, radial light behind the head, fine vertical stripes
yy, xx = np.mgrid[0:P, 0:P]
r = np.sqrt(((xx - P * 0.5) / (P * 0.58)) ** 2 + ((yy - P * 0.44) / (P * 0.58)) ** 2)
c0, c1 = np.array([78, 130, 255]), np.array([20, 58, 186]); t = np.clip(r, 0, 1)[..., None] ** 1.2
g = c0 * (1 - t) + c1 * t
g += (((xx % 40) < 3)[..., None]) * 9 * (1 - np.clip(r, 0, 1))[..., None]
bg = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert("RGBA")
# face centre on the grid ≈ (54, 40) → place it at the canvas centre, slightly above middle
cx, cy = 54, 40
big = grid.resize((108 * Z, 92 * Z), Image.NEAREST)
ox, oy = int(P / 2 - (cx + 0.5) * Z), int(P * 0.47 - (cy + 0.5) * Z)
bg.alpha_composite(big, (ox, oy))
bg.convert("RGB").save(sys.argv[2])
if len(sys.argv) > 3:   # how it reads inside Instagram's circle
    m = Image.new("L", (P, P), 0); ImageDraw.Draw(m).ellipse((0, 0, P - 1, P - 1), fill=255)
    prev = Image.new("RGB", (P, P), (255, 255, 255)); prev.paste(bg.convert("RGB"), (0, 0), m)
    prev.resize((360, 360), Image.LANCZOS).save(sys.argv[3])
print("ok")
