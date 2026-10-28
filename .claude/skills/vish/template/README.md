# Vish reel template (current: "Speed-to-lead" for property agents, v4)

A 1080 × 1920, 30 fps Instagram Reel project built with [HyperFrames](https://hyperframes.heygen.com). The top panel holds editorial motion graphics and the lower panel holds the animated pixel-art presenter. Full-screen takeovers carry the hook, the reliability beat and the closing CTA.

The script, timings and scenes in this folder belong together: `python3 tools/build.py` works straight after a copy. For a new reel, change `tools/script.json`, regenerate the voice and timings, then edit the copy and scenes. The steps are in `../references/reel-pipeline.md`.

## Story structure (every reel)

| Scene | Job | Example (v4) |
| --- | --- | --- |
| `hook` | Name the audience and the pain (takeover, cover frame) | "Property agents: your enquiries go cold while you're out on site visits." |
| `problem` | A relatable moment, in the owner's words | "A buyer enquires at 9 PM… another broker is already talking to them." |
| `solution` | **The turn.** Vish introduces his solution and its number of workflows (light panel) | "That's why I built an AI agent solution for property agents, with four connected workflows." |
| `a1`–`a4` | Each workflow: an ordinal intro, then **at once** what it does | "First, respond to enquiries. Every enquiry… lands in your CRM, and AI replies right away…" |
| `key` | Reliability: connected tools, clear rules, you approve | "The key? Portals, CRM and calendar connected, clear rules, and you approving what matters." |
| `cta` | Standard follow + comment WORKFLOW ending, **never edited** | "Want this workflow built for your business? Follow me and comment workflow…" |

## Voice

The voice is "Vish warm", set in `tools/make_vo.py`: an even blend of Kokoro hm_omega and hm_psi, `en-gb`, speed 0.9 (CTA 1.0), −1 semitone with formants kept, then the clarity chain. `GAP` sets the pause after each scene; the problem → solution turn gets a slightly longer pause.

## Files

| Path | What it is |
| --- | --- |
| `project.config.json` | Video length, brand, colours, fonts, on-screen copy per scene, SFX cues (each tied to a spoken word) |
| `tools/script.json` | One entry per scene: `say` (what Kokoro reads) and `text` (captions) |
| `src/scenes/*.html` | One template per scene; `W.<word>` is the scene-local time of a spoken word |
| `src/presenter.html` | Vish's panel: lip sync, blinks, brows, head moves |
| `tools/build.py` | Writes `index.html` and `compositions/`; presenter anchors near line 133 |
| `tools/write_storyboard.py` | `STORYBOARD.md`; update the `VIS` text per scene |
