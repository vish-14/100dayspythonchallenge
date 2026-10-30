---
name: vish
description: Daily content engine, brand kit and production playbook for "Vish", the pixel-art AI-automation presenter of the Instagram page @vish.workflows (backend: Sri Trilinga Technologies Private Limited), built to win AI automation and AI agent projects from every industry worldwide. Use whenever the user types /vish or /vish daily, asks for today's reel, daily content, reel ideas or research, a lead-magnet PDF guide, captions or posting times, or mentions Vish, @vish.workflows, the pixel character, the automation reels or the WORKFLOW comment CTA, or asks for a new reel, post, caption, bio, profile picture, thumbnail or character art for this page. Holds the exact character design (palette, pixel grid, layers), the page's voice and copy rules, the reel pipeline that worked (HyperFrames + Kokoro voice + MusicGen + Parakeet captions), and the scripts that regenerate the character exactly.
---

# Vish — character and page playbook

## Daily mode (`/vish daily`, "today's reel", or `/vish` with no other request)

Follow `references/daily-run.md` from start to finish:
1. Research and score fresh concepts across all industries (`references/concept-engine.md`).
2. **Get the user's pick.**
3. Write the script (problem → my solution → its workflows, each introduced with "First, … Second, …" and explained at once → CTA) and **get approval**.
4. Make the reel and the topic PDF guide (`references/guide-pdf.md`).
5. Write the post kit: caption, cover, pinned comment, SuperProfile setup and the post time in IST plus world times.
6. Log it in `vish-daily/content-log.md`.

Everything serves leads: `references/lead-engine.md`.

Vish is the on-screen persona of the Instagram page **@vish.workflows** (display name **"Vish | AI Automation"**). He explains practical AI automations to business owners worldwide and invites them to comment **"WORKFLOW"** to get a workflow built. The business behind the page is **Sri Trilinga Technologies Private Limited**, which stays in the background.

## Non-negotiables

1. **Keep Vish identical everywhere.** Never redraw him freehand. Regenerate him with `scripts/make_sprite.py` (layers) and `scripts/make_profile.py` (profile picture). The design spec is in `references/character-bible.md`.
2. **The persona speaks in the first person** ("Follow me… I'll send you…"). The company name never appears in the video, bio or on-screen text. It appears **only once, at the very end of a reel caption**, for SEO (see `references/brand-and-page.md`).
3. **The CTA keyword is `WORKFLOW`** everywhere: voice, on-screen pill, caption, SuperProfile trigger. Follow first, then comment (the auto-DM only reaches followers).
4. **No invented statistics, client results or guaranteed savings.** Example names and values on UI cards are illustrative.
6. **Never impersonate real people.** No real politician, celebrity or public figure as a character, and no cloned or imitated voices of real people (for example the Prime Minister), even as a joke. Channel jingles (TV9, Aaj Tak and so on) are copyrighted too: use the original `siren-police` and `news-sting` sounds instead.
5. **No copyrighted audio.** Voice comes from Kokoro (offline), always the "Vish warm" voice in `template/tools/make_vo.py` (hm_omega + hm_psi blend, en-gb, 0.9×, −1 semitone, clarity chain). Music is original (MusicGen, run locally) or properly licensed. SFX come from the HyperFrames bundle (Pixabay licence).

## What's in this skill

| Path | Use it for |
| --- | --- |
| `references/character-bible.md` | Exact look of Vish: palette hex values, pixel-grid layout, layer list, expressions, do/don't |
| `references/brand-and-page.md` | Handle, name, bio, caption template (SEO), CTA wording, SuperProfile setup, posting times, do/don't |
| `references/reel-pipeline.md` | Step-by-step production of a new reel: script, voice, timing, captions, music, render, QA |
| `scripts/make_sprite.py` | Regenerates every character layer (1080×920 each, 10× pixel scale) plus preview sheets |
| `scripts/make_profile.py` | Regenerates the 1080×1080 Instagram profile picture, centred for the circle crop |
| `assets/character/` | Ready-made layers, `instagram_profile_picture.png`, `character_expressions.png`, `avatar.png` |
| `references/dm-playbook.md` | What commenters get: the guide, SuperProfile settings, every DM message (follower, non-follower, 24 h follow-up, BUILD reply) |
| `references/daily-run.md` | The daily routine: research → Gate 1 concept → Gate 2 script → reel → PDF → post kit → log |
| `references/concept-engine.md` | Research lenses, scoring, rotation rules, the industry map (pains → automations) and buyer hooks |
| `references/lead-engine.md` | Comment → DM → call → proposal → pilot, discovery questions per industry, metrics to track |
| `references/guide-pdf.md` | How to write `guide.json` and build the PDF guide; layout and writing rules |
| `scripts/guide/make_guide.py` | JSON → A4 PDF guide in the house style, with page PNGs and a link check (`render.js`, `guide.css` and bundled Inter fonts beside it) |
| `scripts/make_news_sfx.py` | Regenerates the original police siren (wail → high-low-high yelps → wail) and the breaking-news sting |
| `scripts/make_hindi_vo.py` | Natural Hindi line with AI4Bharat Indic Parler-TTS (needs `HF_TOKEN`); writes several takes to pick by ear |
| `template/hooks/wedding-hook.html` | Optional festive opening: marigold frame, garlands, fairy lights, original bhangra silhouettes, petals; use with `"hook_mode"` and the turban prop |
| `scripts/make_dhol_sfx.py` | Regenerates the original dhol intro and loop |
| `template/hooks/breaking-news-hook.html` | Optional 7-frame breaking-news opening (hard cuts, strobe, slams, shakes); swap it in as `src/scenes/hook.html` |
| `scripts/setup.sh` | One-time install and check of the toolchain and models in a fresh container |
| `assets/content-log.template.md` | Starting point for `vish-daily/content-log.md` |
| `assets/lead-magnet/` | The first guide: web page, PDF and its `4-task-workflow.guide.json` source |
| `template/` | The working HyperFrames reel project (latest: speed-to-lead v4, with hook → problem → solution → 4 workflows → key → CTA), without the large audio files. It builds as-is after a copy |

## Quick recipes

- **Profile picture or avatar:** use `assets/character/instagram_profile_picture.png` as is, or run `python3 scripts/make_profile.py assets/character out.png circle_preview.png`.
- **Character art in a new pose or expression:** combine existing layers (body, head, eyes_*, brows_*, mouth_*, mustache) in that order. For anything new, add it to `make_sprite.py` using only the palette in the character bible, and check it at 1× and 10× before using it.
- **Daily post:** follow `references/daily-run.md`.
- **PDF guide only:** write a `guide.json` (see `references/guide-pdf.md`) and run `scripts/guide/make_guide.py`.
- **New reel:** follow `references/reel-pipeline.md`. Copy `template/` to a new folder, edit `project.config.json` and `tools/script.json`, then run the pipeline.
- **Caption or bio:** use the templates in `references/brand-and-page.md`. Keep the company line last.

When anything here conflicts with a newer instruction from the user, the user wins. Then update this skill's files so the change sticks.
