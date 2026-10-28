---
name: vish
description: Brand kit and production playbook for "Vish", the pixel-art AI-automation presenter of the Instagram page @vish.workflows (backend: Sri Trilinga Technologies Private Limited). Use whenever the user mentions Vish, @vish.workflows, the pixel character, the automation reels, the WORKFLOW comment CTA, or asks for a new reel, post, caption, bio, profile picture, thumbnail or character art for this page. Holds the exact character design (palette, pixel grid, layers), the page's voice and copy rules, the reel pipeline that worked (HyperFrames + Kokoro voice + MusicGen + Parakeet captions), and the scripts that regenerate the character exactly.
---

# Vish — character and page playbook

Vish is the on-screen persona of the Instagram page **@vish.workflows** (display name **"Vish | AI Automation"**). He explains practical AI automations to business owners worldwide and invites them to comment **"WORKFLOW"** to get a workflow built. The business behind the page is **Sri Trilinga Technologies Private Limited**, which stays in the background.

## Non-negotiables

1. **Keep Vish identical everywhere.** Never redraw him freehand. Regenerate him with `scripts/make_sprite.py` (layers) and `scripts/make_profile.py` (profile picture). The design spec is in `references/character-bible.md`.
2. **The persona speaks in the first person** ("Follow me… I'll send you…"). The company name never appears in the video, bio or on-screen text. It appears **only once, at the very end of a reel caption**, for SEO (see `references/brand-and-page.md`).
3. **The CTA keyword is `WORKFLOW`** everywhere: voice, on-screen pill, caption, SuperProfile trigger. Follow first, then comment (the auto-DM only reaches followers).
4. **No invented statistics, client results or guaranteed savings.** Example names and values on UI cards are illustrative.
5. **No copyrighted audio.** Voice comes from Kokoro (offline). Music is original (MusicGen, run locally) or properly licensed. SFX come from the HyperFrames bundle (Pixabay licence).

## What's in this skill

| Path | Use it for |
| --- | --- |
| `references/character-bible.md` | Exact look of Vish: palette hex values, pixel-grid layout, layer list, expressions, do/don't |
| `references/brand-and-page.md` | Handle, name, bio, caption template (SEO), CTA wording, SuperProfile setup, posting times, do/don't |
| `references/reel-pipeline.md` | Step-by-step production of a new reel: script, voice, timing, captions, music, render, QA |
| `scripts/make_sprite.py` | Regenerates every character layer (1080×920 each, 10× pixel scale) plus preview sheets |
| `scripts/make_profile.py` | Regenerates the 1080×1080 Instagram profile picture, centred for the circle crop |
| `assets/character/` | Ready-made layers, `instagram_profile_picture.png`, `character_expressions.png`, `avatar.png` |
| `template/` | The working HyperFrames reel project (scenes, presenter, captions, config, tools, SFX), without the large audio files |

## Quick recipes

- **Profile picture or avatar:** use `assets/character/instagram_profile_picture.png` as is, or run `python3 scripts/make_profile.py assets/character out.png circle_preview.png`.
- **Character art in a new pose or expression:** combine existing layers (body, head, eyes_*, brows_*, mouth_*, mustache) in that order. For anything new, add it to `make_sprite.py` using only the palette in the character bible, and check it at 1× and 10× before using it.
- **New reel:** follow `references/reel-pipeline.md`. Copy `template/` to a new folder, edit `project.config.json` and `tools/script.json`, then run the pipeline.
- **Caption or bio:** use the templates in `references/brand-and-page.md`. Keep the company line last.

When anything here conflicts with a newer instruction from the user, the user wins. Then update this skill's files so the change sticks.
