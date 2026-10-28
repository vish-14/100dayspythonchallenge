"""Draws the original pixel-art presenter as stacked layers.

Usage: python3 tools/make_sprite.py assets/presenter [preview.png]

Every layer is drawn on a 108x92 pixel grid, then scaled 10x with nearest-neighbour
so the edges stay crisp (1080x920 per layer). Layers share one canvas so they stack
with no offsets: body, head, eyes (open/half/closed), brows (neutral/up) and six
mouth shapes (rest, B small, A open, E wide, O round, M pressed).
"""
import os, sys
from PIL import Image, ImageDraw

W, H, SCALE = 108, 92, 10
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

C = {
    "outline": (22, 18, 30, 255),
    "skin": (196, 134, 92, 255), "skin_lt": (216, 158, 114, 255), "skin_dk": (160, 102, 66, 255), "stubble": (139, 92, 64, 255),
    "hair": (28, 24, 34, 255), "hair_lt": (60, 54, 72, 255),
    "jacket": (28, 40, 82, 255), "jacket_dk": (20, 28, 60, 255), "jacket_lt": (46, 64, 120, 255),
    "shirt": (242, 239, 230, 255), "shirt_dk": (210, 204, 190, 255),
    "frame": (30, 30, 40, 255), "lens": (190, 215, 255, 70), "glint": (255, 255, 255, 200),
    "eye_w": (246, 244, 238, 255), "pupil": (28, 22, 30, 255),
    "lip": (140, 74, 58, 255), "mouth": (70, 22, 30, 255), "teeth": (246, 242, 232, 255), "tongue": (196, 86, 86, 255),
    "rim": (140, 185, 255, 255),
}


def canvas():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def outline(img, col=C["outline"]):
    """1px pixel-art outline around everything opaque in the layer."""
    src = img.load(); out = img.copy(); o = out.load()
    for y in range(H):
        for x in range(W):
            if src[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H and src[nx, ny][3] > 200:
                        o[x, y] = col; break
    return out


def rim(img, col=C["rim"], side=1):
    """Light from the blue backdrop: a 1px rim just inside the right-hand silhouette edge."""
    src = img.load(); out = img.copy(); o = out.load()
    for y in range(H):
        for x in range(W):
            if src[x, y][3] > 200 and src[x, y][:3] != C["outline"][:3]:
                nx = x + side
                if 0 <= nx < W and src[nx, y][3] > 200 and src[nx, y][:3] == C["outline"][:3]:
                    o[x, y] = col
    return out


def save(img, name):
    img.resize((W * SCALE, H * SCALE), Image.NEAREST).save(os.path.join(OUT, name + ".png"))
    return img


# ---------------------------------------------------------------- body
body = canvas(); d = ImageDraw.Draw(body)
d.rectangle((48, 56, 60, 68), fill=C["skin_dk"])                                     # neck
d.polygon([(10, 92), (16, 76), (30, 68), (46, 64), (62, 64), (78, 68), (92, 76), (98, 92)], fill=C["jacket"])
d.polygon([(46, 64), (62, 64), (59, 92), (49, 92)], fill=C["shirt"])                  # shirt
d.polygon([(46, 64), (54, 70), (49, 72)], fill=C["shirt_dk"]); d.polygon([(62, 64), (54, 70), (59, 72)], fill=C["shirt_dk"])  # collar
d.polygon([(44, 65), (49, 72), (52, 90), (46, 92), (40, 76)], fill=C["jacket_dk"])   # lapels
d.polygon([(64, 65), (59, 72), (56, 90), (62, 92), (68, 76)], fill=C["jacket_dk"])
d.line([(16, 78), (30, 70)], fill=C["jacket_lt"]); d.line([(92, 78), (80, 71)], fill=C["jacket_lt"])
for y in (76, 84):
    d.point((54, y), fill=C["shirt_dk"])
d.rectangle((26, 84, 27, 92), fill=C["jacket_dk"]); d.rectangle((81, 84, 82, 92), fill=C["jacket_dk"])  # arm seams
body = rim(outline(body))
save(body, "body")

# ---------------------------------------------------------------- head (no eyes, brows or mouth)
head = canvas(); d = ImageDraw.Draw(head)
d.ellipse((31, 35, 38, 48), fill=C["skin_dk"]); d.ellipse((70, 35, 77, 48), fill=C["skin_dk"])   # ears
d.ellipse((34, 13, 74, 41), fill=C["hair"])                                                       # hair mass
d.ellipse((36, 20, 72, 61), fill=C["skin"])                                                       # face
d.ellipse((38, 22, 54, 40), fill=C["skin_lt"])                                                    # forehead light
d.polygon([(35, 34), (37, 22), (46, 15), (60, 14), (70, 19), (73, 28), (73, 35), (69, 27), (60, 23), (52, 24), (44, 25), (39, 30)], fill=C["hair"])  # side-part fringe
d.line([(44, 18), (56, 16)], fill=C["hair_lt"]); d.line([(46, 20), (52, 19)], fill=C["hair_lt"])
d.rectangle((35, 33, 37, 41), fill=C["hair"]); d.rectangle((71, 33, 73, 41), fill=C["hair"])      # sideburns
# short beard / stubble along the jaw (dithered)
hp = head.load()
for y in range(48, 62):
    for x in range(37, 72):
        if hp[x, y][:3] in (C["skin"][:3], C["skin_lt"][:3]):
            inside = ((x - 54) / 18.0) ** 2 + ((y - 41) / 20.5) ** 2
            if inside > 0.62 and (x + y) % 2 == 0:
                hp[x, y] = C["stubble"]
d.rectangle((53, 43, 54, 48), fill=C["skin_dk"]); d.point((52, 48), fill=C["skin_dk"]); d.point((55, 48), fill=C["skin_dk"])  # nose
head = outline(head)
# glasses on top of the outline pass (thin frames)
tint = canvas(); td = ImageDraw.Draw(tint)
for x0 in (41, 57):
    td.rectangle((x0 + 1, 36, x0 + 9, 42), fill=C["lens"])          # blended over the skin, not punched through
head.alpha_composite(tint)
d = ImageDraw.Draw(head)
for x0 in (41, 57):
    d.rectangle((x0, 35, x0 + 10, 43), outline=C["frame"])
    d.point((x0 + 2, 37), fill=C["glint"]); d.point((x0 + 3, 37), fill=C["glint"])
d.line([(52, 38), (56, 38)], fill=C["frame"])
d.line([(37, 38), (40, 38)], fill=C["frame"]); d.line([(68, 38), (71, 38)], fill=C["frame"])
head = rim(head)
save(head, "head")

# ---------------------------------------------------------------- eyes
def eyes(state):
    im = canvas(); d = ImageDraw.Draw(im)
    for x0 in (44, 60):
        if state == "open":
            d.rectangle((x0, 38, x0 + 4, 40), fill=C["eye_w"]); d.rectangle((x0 + 1, 38, x0 + 3, 40), fill=C["pupil"])
            d.point((x0 + 1, 38), fill=C["eye_w"])
        elif state == "half":
            d.rectangle((x0, 39, x0 + 4, 40), fill=C["pupil"]); d.line([(x0, 38), (x0 + 4, 38)], fill=C["skin_dk"])
        else:
            d.line([(x0, 40), (x0 + 4, 40)], fill=C["pupil"])
    return im


for s in ("open", "half", "closed"):
    save(eyes(s), f"eyes_{s}")


def brows(up):
    im = canvas(); d = ImageDraw.Draw(im); y = 32 - (2 if up else 0)
    d.rectangle((42, y, 49, y + 1), fill=C["hair"]); d.rectangle((59, y, 66, y + 1), fill=C["hair"])
    if up:
        d.point((42, y + 2), fill=C["hair"]); d.point((66, y + 2), fill=C["hair"])
    return im


save(brows(False), "brows_neutral"); save(brows(True), "brows_up")


# ---------------------------------------------------------------- mouths (centre 54, 53)
def mouth(kind):
    im = canvas(); d = ImageDraw.Draw(im)
    if kind == "rest":            # relaxed smile
        d.line([(50, 53), (58, 53)], fill=C["lip"]); d.point((49, 52), fill=C["lip"]); d.point((59, 52), fill=C["lip"])
    elif kind == "M":             # lips pressed (m, b, p)
        d.line([(50, 53), (58, 53)], fill=C["mouth"]); d.line([(51, 54), (57, 54)], fill=C["lip"])
    elif kind == "B":             # slightly open
        d.rectangle((50, 52, 58, 54), fill=C["mouth"]); d.line([(51, 52), (57, 52)], fill=C["teeth"])
        d.line([(50, 55), (58, 55)], fill=C["lip"])
    elif kind == "A":             # open (ah)
        d.ellipse((49, 50, 59, 58), fill=C["mouth"]); d.line([(51, 51), (57, 51)], fill=C["teeth"])
        d.rectangle((52, 56, 56, 57), fill=C["tongue"]); d.line([(51, 59), (57, 59)], fill=C["lip"])
    elif kind == "E":             # wide (ee, s)
        d.rectangle((48, 52, 60, 55), fill=C["mouth"]); d.line([(49, 52), (59, 52)], fill=C["teeth"])
        d.line([(49, 55), (59, 55)], fill=C["teeth"]); d.point((47, 51), fill=C["lip"]); d.point((61, 51), fill=C["lip"])
    elif kind == "O":             # round (oo, w)
        d.ellipse((51, 50, 57, 57), fill=C["lip"]); d.ellipse((52, 51, 56, 56), fill=C["mouth"])
    return im


for k in ("rest", "M", "B", "A", "E", "O"):
    save(mouth(k), f"mouth_{k}")

# ---------------------------------------------------------------- preview sheet
if len(sys.argv) > 2:
    tiles = []
    for e, b, m in (("open", "neutral", "rest"), ("open", "up", "A"), ("half", "neutral", "E"), ("closed", "neutral", "O"), ("open", "neutral", "B"), ("open", "neutral", "M")):
        t = Image.new("RGBA", (W, H), (34, 87, 239, 255))
        for layer in (body, head, eyes(e), brows(b == "up"), mouth(m)):
            t.alpha_composite(layer)
        tiles.append(t.resize((W * 5, H * 5), Image.NEAREST))
    sheet = Image.new("RGBA", (W * 5 * 3, H * 5 * 2))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % 3) * W * 5, (i // 3) * H * 5))
    sheet.save(sys.argv[2])
print("ok")
