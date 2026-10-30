# Vish — character bible

Vish is an **original pixel-art character**. He is loosely inspired by the page owner's features (short dense curly hair, slim face, thick brows, thin mustache curving down at the corners), but he is a cartoon, **not a portrait**, and does **not** copy the owner's clothes.

## Look at a glance

| Feature | Spec |
| --- | --- |
| Style | Clean pixel art, 1px dark outline, flat colours, one consistent skin tone, blue rim light on hair and jacket only |
| Hair | Short, dense black curls with volume on top, a rounded dome with small curls along the top edge, short neat sideburns, small "c"-shaped curl highlights |
| Face | Slim with a defined jaw, slightly prominent ears, thick straight brows, dark eyes with a white highlight pixel, a short straight nose line |
| Mustache | Thin, black, straight across with the corners curving down. Its own layer, always drawn above the mouth |
| Skin | **One even light brown** (#CE966C) across face, ears and neck. Only small details use the deeper tones. No highlight patches, no cheek shading blocks |
| Expression | Friendly and approachable: relaxed half smile at rest |
| Outfit | Navy jacket with darker lapels, light-blue open-collar shirt, visible neck. Never the owner's real outfit |
| Background | Electric-blue panel (#2257EF) with a soft radial glow and faint vertical stripes |

## Palette (RGB hex)

| Name | Hex | Used for |
| --- | --- | --- |
| outline | #140E16 | 1px silhouette outline |
| skin | #CE966C | Face, ears, neck, eyelids (the only skin fill) |
| skin_dk | #B67E58 | Nose line, jaw shadow on the neck, small details |
| skin_dd | #A06848 | Nostril dots, inner ear lines |
| hair | #161218 | Hair, brows, mustache |
| hair_md | #28202A | Curl texture (mid), mustache top edge |
| hair_lt | #423646 | Curl highlight pixel |
| jacket | #1E2A54 | Jacket |
| jacket_dk | #141D3E | Lapels, seams |
| jacket_lt | #30427A | Shoulder highlight |
| shirt | #C4DEF6 | Shirt |
| shirt_dk | #96B8DC | Collar shadow, buttons |
| eye_w | #F4F0E8 | Eye white |
| pupil | #1A1014 | Pupils, lash line |
| lip | #9C5648 | Lips |
| mouth | #42141C | Mouth interior |
| teeth | #ECE6DC | Teeth |
| tongue | #BA5454 | Tongue |
| rim | #8CB9FF | Rim light (hair and jacket edges only, never on skin) |

\*The source of truth for every colour is the `C = {...}` dictionary in `scripts/make_sprite.py`.

Brand colours around him: electric blue #2257EF, near-black #0B1016, off-white #F5F5F7, grey #8A93A3.

## Pixel grid

- Canvas: **108 × 92 pixels**, scaled **10×** with nearest-neighbour, so each layer is **1080 × 920**. In the reel, the presenter panel occupies y = 1010–1920 of a 1080×1920 frame, with the sprite top at −10 px.
- Head centre ≈ (54, 40). Eyes at y = 37–39 (left x 43–48, right x 59–64). Brows at y = 31–32. Mustache at y = 49–52 (x 47–61). Mouth centre (54, 53). Neck at x 49–59, y 56–68. Shoulders from y ≈ 64.

## Layers (stack in this order)

1. `body` (jacket, shirt, neck)
2. `head` (hair, face, ears, nose)
3. `eyes_open` | `eyes_half` | `eyes_closed`
4. `brows_neutral` | `brows_up`
5. `mouth_rest` | `mouth_M` (pressed) | `mouth_B` (small) | `mouth_A` (open) | `mouth_E` (wide) | `mouth_O` (round)
6. `mustache` (always on top)
7. Optional props for the news-anchor hook: `prop_desk` (near-black desk with a red name plate, covers the lower torso) and `prop_mic` (desk mic with a red channel flag, in front of the chest, never over the face). Brand colours only; drawn in `make_sprite.py`. `prop_turban`: a wedding safa (saffron and red wraps, gold band on the forehead, jewelled kalgi with a plume, loose end on the right) for festive hooks; it sits above the brows (rows 3–26) so the face stays readable, and moves with the head layer. `prop_dhol` (wooden barrel with gold rope lacing and two cream heads, red strap, slung across the chest, rows 66–92) with stick layers `prop_dagga` (thick curved bass stick, pivot at grid 10,90 → 100px 900px) and `prop_tilli` (thin cane, pivot 100,90 → 1000px 900px); the sticks rotate on the beat in hook mode.

## Animation rules

- **Lip sync:** one mouth shape per frame (30 fps), chosen from the voice's loudness and spectrum (see `references/reel-pipeline.md`). Hold any shape for at least 2 frames.
- **Blinks:** every 2.7–4 s (half, closed, half over about 4 frames).
- **Brows up:** for about 0.75 s on headline numbers and emphasis words.
- **Head movement:** only small shifts in whole sprite pixels (10 px), at most once per scene. No continuous bobbing, no rotation (it breaks the pixel grid).

## Do

- Keep proportions, palette and outfit identical across every reel and graphic.
- Reuse the shipped layers. If something new is needed (a wave, a thumbs-up, a new outfit for a special post), draw it in `make_sprite.py` with the same palette and outline rules.
- Check every new asset at full size **and** at phone size.

## Don't

- Don't use AI image generators to "re-imagine" Vish for regular posts; the look will drift. (One-off promotional art is fine if it is clearly matched to this bible.)
- Don't add skin shading patches, gradients, blur, anti-aliasing or photo textures.
- Don't put the rim light on the skin.
- Don't copy the owner's real clothes or photograph.
