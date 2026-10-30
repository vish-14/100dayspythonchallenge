"""Draws the original pixel-art presenter as stacked layers.

Usage: python3 tools/make_sprite.py assets/presenter [preview.png] [profile.png]

An original character, loosely inspired by a reference face (short dense curly hair,
slim face, thick brows, thin mustache curving down at the corners, warm brown skin);
not a copy of any photo or outfit. Every layer is drawn on a 108x92 pixel grid, then
scaled 10x with nearest-neighbour so edges stay crisp (1080x920 per layer).
Layers: body, head, eyes (open/half/closed), brows (neutral/up), mouths
(rest, M, B, A, E, O) and a mustache layer that sits above the mouths.
"""
import os, sys, math
from PIL import Image, ImageDraw

W, H, SCALE = 108, 92, 10
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

C = {
    "outline": (20, 14, 22, 255),
    "skin": (206, 150, 108, 255), "skin_lt": (206, 150, 108, 255), "skin_dk": (182, 126, 88, 255), "skin_dd": (160, 104, 72, 255),
    "hair": (22, 18, 24, 255), "hair_md": (40, 32, 42, 255), "hair_lt": (66, 54, 70, 255),
    "jacket": (30, 42, 84, 255), "jacket_dk": (20, 29, 62, 255), "jacket_lt": (48, 66, 122, 255),
    "shirt": (196, 222, 246, 255), "shirt_dk": (150, 184, 220, 255),
    "eye_w": (244, 240, 232, 255), "pupil": (26, 16, 20, 255),
    "lip": (156, 86, 72, 255), "mouth": (66, 20, 28, 255), "teeth": (236, 230, 220, 255), "tongue": (186, 84, 84, 255),
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


def rim(img, col=C["rim"]):
    """Light from the blue backdrop: a 1px rim just inside the right-hand silhouette edge."""
    src = img.load(); out = img.copy(); o = out.load()
    for y in range(H):
        for x in range(W - 1):
            if src[x, y][3] > 200 and src[x, y][:3] not in (C["outline"][:3], C["skin"][:3]) and src[x + 1, y][:3] == C["outline"][:3] and src[x + 1, y][3] > 200:
                o[x, y] = col
    return out


def save(img, name):
    img.resize((W * SCALE, H * SCALE), Image.NEAREST).save(os.path.join(OUT, name + ".png"))
    return img


# ---------------------------------------------------------------- body: navy jacket, light-blue open-collar shirt
body = canvas(); d = ImageDraw.Draw(body)
d.rectangle((49, 56, 59, 68), fill=C["skin"])                                        # neck
d.line([(50, 61), (58, 61)], fill=C["skin_dk"])                                      # soft jaw shadow on the neck
d.polygon([(10, 92), (16, 76), (30, 68), (46, 64), (62, 64), (78, 68), (92, 76), (98, 92)], fill=C["jacket"])
d.polygon([(46, 64), (62, 64), (60, 92), (48, 92)], fill=C["shirt"])                  # shirt
d.polygon([(46, 63), (54, 71), (48, 73)], fill=C["shirt_dk"]); d.polygon([(62, 63), (54, 71), (60, 73)], fill=C["shirt_dk"])  # open collar
d.polygon([(51, 64), (57, 64), (54, 69)], fill=C["skin"])                             # open neck
d.polygon([(44, 65), (49, 73), (52, 90), (46, 92), (40, 76)], fill=C["jacket_dk"])   # lapels
d.polygon([(64, 65), (59, 73), (56, 90), (62, 92), (68, 76)], fill=C["jacket_dk"])
d.line([(16, 78), (30, 70)], fill=C["jacket_lt"]); d.line([(92, 78), (80, 71)], fill=C["jacket_lt"])
d.point((54, 80), fill=C["shirt_dk"]); d.point((54, 87), fill=C["shirt_dk"])
d.rectangle((26, 84, 27, 92), fill=C["jacket_dk"]); d.rectangle((81, 84, 82, 92), fill=C["jacket_dk"])
body = rim(outline(body))
save(body, "body")

# ---------------------------------------------------------------- head: slim face, curly hair, prominent ears
head = canvas(); d = ImageDraw.Draw(head)
# hair mass first (behind the face): a rounded curly crown with a bumpy silhouette
d.ellipse((35, 11, 73, 34), fill=C["hair"])
for i, cx in enumerate(range(41, 69, 3)):     # small curls along the top edge of the dome
    cy = 12 + int(4 * ((cx - 54) / 14) ** 2) + (i % 2)
    d.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=C["hair"])
d.ellipse((31, 35, 38, 47), fill=C["skin"]); d.ellipse((70, 35, 77, 47), fill=C["skin"])                # ears
d.line([(34, 38), (34, 44)], fill=C["skin_dd"]); d.line([(74, 38), (74, 44)], fill=C["skin_dd"])        # inner ear
d.ellipse((37, 20, 71, 62), fill=C["skin"])                                                             # face
d.polygon([(40, 50), (68, 50), (63, 60), (54, 63), (45, 60)], fill=C["skin"])                          # slimmer jaw
# hairline: a gently rounded fringe edge, forehead clear above the brows
d.polygon([(36, 32), (37, 24), (43, 20), (54, 19), (65, 20), (71, 24), (72, 32), (70, 27), (63, 24), (54, 23), (45, 24), (38, 27)], fill=C["hair"])
d.rectangle((37, 28, 38, 33), fill=C["hair"]); d.rectangle((70, 28, 71, 33), fill=C["hair"])          # short sideburns
hp = head.load()
for y in range(7, 30):           # curl texture: small irregular "c" shaped highlights
    for x in range(36, 72):
        k = (x * 7 + y * 13) % 17
        if (y % 3 == 1) and k in (0, 5) and hp[x, y][:3] == C["hair"][:3] and hp[x + 2, y][:3] == C["hair"][:3] and hp[x + 1, y - 1][:3] == C["hair"][:3]:
            hp[x, y] = C["hair_md"]; hp[x + 1, y - 1] = C["hair_lt"]; hp[x + 2, y] = C["hair_md"]
# nose and cheek shading
d.line([(54, 42), (54, 46)], fill=C["skin_dk"]); d.point((52, 48), fill=C["skin_dd"]); d.point((56, 48), fill=C["skin_dd"])
d.line([(53, 48), (55, 48)], fill=C["skin_dk"])
head = rim(outline(head))
save(head, "head")

# ---------------------------------------------------------------- eyes
def eyes(state):
    im = canvas(); d = ImageDraw.Draw(im)
    for x0 in (43, 59):
        if state == "open":
            d.rectangle((x0, 37, x0 + 5, 39), fill=C["eye_w"]); d.rectangle((x0 + 2, 37, x0 + 4, 39), fill=C["pupil"])
            d.point((x0 + 3, 37), fill=(255, 255, 255, 255)); d.line([(x0 + 1, 36), (x0 + 4, 36)], fill=C["pupil"])
        elif state == "half":
            d.rectangle((x0, 36, x0 + 5, 37), fill=C["skin"]); d.rectangle((x0, 38, x0 + 5, 39), fill=C["pupil"])
        else:
            d.rectangle((x0, 36, x0 + 5, 38), fill=C["skin"]); d.line([(x0, 39), (x0 + 5, 39)], fill=C["pupil"])
    return im


for s in ("open", "half", "closed"):
    save(eyes(s), f"eyes_{s}")


def brows(up):   # thick, slightly angled
    im = canvas(); d = ImageDraw.Draw(im); y = 31 - (2 if up else 0)
    d.rectangle((43, y, 50, y + 1), fill=C["hair"]); d.point((42, y + 1), fill=C["hair"])
    d.rectangle((58, y, 65, y + 1), fill=C["hair"]); d.point((66, y + 1), fill=C["hair"])
    return im


save(brows(False), "brows_neutral"); save(brows(True), "brows_up")

# ---------------------------------------------------------------- mustache (above the mouths): thin, curving down at the corners
def mustache():
    im = canvas(); d = ImageDraw.Draw(im)
    d.line([(49, 50), (59, 50)], fill=C["hair"]); d.line([(50, 49), (58, 49)], fill=C["hair_md"])
    d.point((48, 51), fill=C["hair"]); d.point((47, 52), fill=C["hair"]); d.point((60, 51), fill=C["hair"]); d.point((61, 52), fill=C["hair"])
    return im


save(mustache(), "mustache")


# ---------------------------------------------------------------- mouths (centre 54, 53), all below the mustache
def mouth(kind):
    im = canvas(); d = ImageDraw.Draw(im)
    if kind == "rest":            # relaxed half smile
        d.line([(51, 54), (57, 54)], fill=C["lip"]); d.point((50, 53), fill=C["lip"]); d.point((58, 53), fill=C["lip"])
        d.line([(52, 56), (56, 56)], fill=C["skin_dk"])
    elif kind == "M":
        d.line([(51, 53), (57, 53)], fill=C["mouth"]); d.line([(52, 54), (56, 54)], fill=C["lip"])
    elif kind == "B":
        d.rectangle((51, 52, 57, 54), fill=C["mouth"]); d.line([(52, 52), (56, 52)], fill=C["teeth"]); d.line([(51, 55), (57, 55)], fill=C["lip"])
    elif kind == "A":
        d.ellipse((50, 51, 58, 58), fill=C["mouth"]); d.line([(52, 52), (56, 52)], fill=C["teeth"])
        d.rectangle((52, 56, 56, 57), fill=C["tongue"]); d.line([(52, 59), (56, 59)], fill=C["lip"])
    elif kind == "E":
        d.rectangle((50, 52, 58, 55), fill=C["mouth"]); d.line([(51, 52), (57, 52)], fill=C["teeth"])
        d.line([(51, 55), (57, 55)], fill=C["teeth"]); d.line([(51, 56), (57, 56)], fill=C["lip"])
    elif kind == "O":
        d.ellipse((51, 51, 57, 57), fill=C["lip"]); d.ellipse((52, 52, 56, 56), fill=C["mouth"])
    return im


for k in ("rest", "M", "B", "A", "E", "O"):
    save(mouth(k), f"mouth_{k}")

# ---------------------------------------------------------------- props (news-anchor look, optional layers)
# Brand colours only: near-black desk, grey metal, news red plate. Drawn on the same grid, same 1px outline.
P = {"desk": (11, 16, 22, 255), "desk_top": (58, 66, 82, 255), "desk_edge": (88, 98, 118, 255),
     "red": (227, 38, 43, 255), "red_dk": (170, 24, 30, 255), "metal": (138, 147, 163, 255), "metal_dk": (90, 98, 112, 255),
     "mic": (30, 30, 36, 255), "grille": (70, 72, 82, 255)}


def desk():
    im = canvas(); d = ImageDraw.Draw(im)
    d.rectangle((0, 76, 107, 91), fill=P["desk"])           # front panel
    d.rectangle((0, 73, 107, 75), fill=P["desk_top"])       # desktop
    d.line((0, 76, 107, 76), fill=P["desk_edge"])            # front edge highlight
    d.rectangle((30, 80, 77, 88), fill=P["red"])            # name plate (text is added in HTML)
    d.line((30, 88, 77, 88), fill=P["red_dk"])
    return outline(im)


def mic():
    im = canvas(); d = ImageDraw.Draw(im)
    d.rectangle((30, 71, 38, 73), fill=P["metal_dk"])       # base on the desk
    for i in range(5):                                       # short stem
        d.point((34, 70 - i), fill=P["metal"]); d.point((35, 70 - i), fill=P["metal"])
    d.rectangle((31, 62, 38, 65), fill=P["red"])            # channel flag
    d.ellipse((31, 54, 38, 62), fill=P["mic"])              # mic head, in front of the chest, clear of the face
    for gx, gy in ((33, 56), (35, 56), (32, 58), (34, 58), (36, 58), (33, 60), (35, 60)):
        d.point((gx, gy), fill=P["grille"])
    return outline(im)


save(desk(), "prop_desk"); save(mic(), "prop_mic")

# wedding safa (turban) for festive hooks: saffron and red wraps, gold band, jewelled kalgi with a plume
T = {"saffron": (240, 140, 0, 255), "red": (201, 42, 42, 255), "maroon": (150, 20, 40, 255), "gold": (242, 201, 76, 255),
     "gold_dk": (196, 148, 32, 255), "cream": (255, 244, 214, 255), "jewel": (224, 49, 49, 255)}


def turban():
    im = canvas(); d = ImageDraw.Draw(im)
    d.ellipse((30, 3, 78, 36), fill=T["saffron"])               # dome, a little larger than the hair
    d.rectangle((30, 27, 78, 40), fill=(0, 0, 0, 0))             # flat base at row 26, just above the brows
    px = im.load()
    for y in range(3, 27):                                       # diagonal wraps
        for x in range(30, 79):
            if px[x, y][3] and ((x + 2 * y) // 4) % 3 == 0:
                px[x, y] = T["red"]
            elif px[x, y][3] and ((x + 2 * y) // 4) % 3 == 1 and y > 14:
                px[x, y] = T["maroon"]
    d.rectangle((31, 23, 77, 26), fill=T["gold"])                # gold band on the forehead
    for x in range(33, 77, 4):
        d.point((x, 24), fill=T["gold_dk"]); d.point((x + 1, 25), fill=T["gold_dk"])
    d.rectangle((74, 20, 79, 31), fill=T["red"])                 # loose end hanging at the side
    d.line((74, 31, 79, 31), fill=T["gold"])
    d.ellipse((51, 11, 58, 18), fill=T["gold"])                  # kalgi brooch
    d.ellipse((53, 13, 56, 16), fill=T["jewel"])
    for i in range(9):                                           # plume curving up and right
        d.point((56 + i // 2, 11 - i), fill=T["cream"]); d.point((57 + i // 2, 11 - i), fill=T["cream"])
    d.point((61, 2), fill=T["gold"])
    return outline(im)


save(turban(), "prop_turban")


# wedding dhol for festive hooks: a barrel drum slung across the chest, plus two sticks (thick dagga for the bass head on
# the left, thin tilli cane for the treble head on the right) drawn as their own layers so they can strike on the beat
D = {"wood": (150, 52, 24, 255), "wood_dk": (110, 34, 16, 255), "wood_lt": (190, 80, 36, 255), "skin": (246, 228, 190, 255),
     "skin_dk": (214, 190, 146, 255), "rope": (242, 201, 76, 255), "strap": (201, 42, 42, 255), "stick": (120, 72, 40, 255), "cane": (214, 176, 110, 255)}


def dhol():
    im = canvas(); d = ImageDraw.Draw(im)
    d.polygon([(30, 66), (36, 66), (78, 82), (72, 82)], fill=D["strap"])        # strap from the left shoulder
    d.rounded_rectangle((26, 72, 82, 92), radius=6, fill=D["wood"])              # barrel
    d.rectangle((28, 74, 80, 76), fill=D["wood_lt"])                             # top highlight
    d.rectangle((28, 89, 80, 92), fill=D["wood_dk"])
    for x in range(32, 78, 6):                                                   # gold rope lacing in a zigzag
        d.line((x, 74, x + 3, 90), fill=D["rope"]); d.line((x + 3, 90, x + 6, 74), fill=D["rope"])
    d.ellipse((18, 70, 32, 92), fill=D["skin"]); d.ellipse((21, 74, 29, 88), fill=D["skin_dk"])   # bass head (left)
    d.ellipse((77, 72, 89, 92), fill=D["skin"]); d.ellipse((80, 76, 86, 88), fill=D["skin_dk"])   # treble head (right)
    d.ellipse((17, 69, 33, 93), outline=D["rope"]); d.ellipse((76, 71, 90, 93), outline=D["rope"])
    return outline(im)


def dagga():   # thick curved bass stick, pivot near the bottom-left (hand) at (10, 90)
    im = canvas(); d = ImageDraw.Draw(im)
    pts = [(10, 90), (12, 86), (14, 82), (17, 79), (20, 77), (23, 76)]
    for i in range(len(pts) - 1):
        d.line((pts[i], pts[i + 1]), fill=D["stick"], width=3)
    d.ellipse((21, 74, 26, 79), fill=D["stick"])
    return outline(im)


def tilli():   # thin straight cane, pivot near the bottom-right (hand) at (100, 90)
    im = canvas(); d = ImageDraw.Draw(im)
    d.line((100, 90, 86, 74), fill=D["cane"], width=2)
    return outline(im)


save(dhol(), "prop_dhol"); save(dagga(), "prop_dagga"); save(tilli(), "prop_tilli")

# ---------------------------------------------------------------- previews
if len(sys.argv) > 2:
    tiles = []
    for e, b, m in (("open", False, "rest"), ("open", True, "A"), ("half", False, "E"), ("closed", False, "O"), ("open", False, "B"), ("open", False, "M")):
        t = Image.new("RGBA", (W, H), (34, 87, 239, 255))
        for layer in (body, head, eyes(e), brows(b), mouth(m), mustache()):
            t.alpha_composite(layer)
        tiles.append(t.resize((W * 5, H * 5), Image.NEAREST))
    sheet = Image.new("RGBA", (W * 5 * 3, H * 5 * 2))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % 3) * W * 5, (i // 3) * H * 5))
    sheet.save(sys.argv[2])
if len(sys.argv) > 3:     # 1080x1080 profile picture on the brand blue
    import numpy as np
    P = 1080; yy, xx = np.mgrid[0:P, 0:P]
    r = np.sqrt(((xx - P * 0.5) / (P * 0.62)) ** 2 + ((yy - P * 0.42) / (P * 0.62)) ** 2)
    c0, c1 = np.array([66, 119, 255]), np.array([22, 63, 194]); t = np.clip(r, 0, 1)[..., None]
    g = c0 * (1 - t) + c1 * t; g += (((xx % 46) < 3)[..., None]) * 11
    bg = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert("RGBA")
    ch = canvas()
    for layer in (body, head, eyes("open"), brows(False), mouth("rest"), mustache()):
        ch.alpha_composite(layer)
    crop = ch.crop((14, 2, 94, 92)).resize((80 * 12, 90 * 12), Image.NEAREST)
    bg.alpha_composite(crop, ((P - crop.width) // 2, P - crop.height))
    bg.convert("RGB").save(sys.argv[3])
print("ok")
