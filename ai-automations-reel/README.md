# Four boring tasks: AI automation reel

A 54-second, 1080 × 1920, 30 fps Instagram Reel built with [HyperFrames](https://hyperframes.heygen.com). It uses a split screen: editorial motion graphics in the top panel and an animated pixel-art presenter in the lower panel, with full-screen takeovers for the hook, the reliability beat and the closing call to action.

**Ending (no company name or emails on screen):** a 12-second call to action built for an auto-DM tool such as SuperProfile, which only replies to followers. Step 1: Follow (the button clicks to “Following ✓”). Step 2: comment “WORKFLOW” (it types and posts). Then a DM arrives: “Your workflow guide is here ✓”. All motion ends about 7 s in and the frame holds to the end. The keyword is in `project.config.json` → `copy.cta.typed` (and in the voiceover script `tools/script.json`).

## Deliverables

| File | What it is |
| --- | --- |
| `ai_automations_sri_final.mp4` | Final video: H.264, AAC stereo 48 kHz, 54.0 s, 30 fps |
| `ai_automations_voiceover.wav` | The voiceover alone (24 kHz mono) |
| `ai_automations_captions.srt` | Phrase-level captions, timed from the real voiceover |
| `STORYBOARD.md` | Timestamped script and storyboard |
| `project.config.json` | Central config: copy, colours, fonts, contact details, asset paths, audio levels, sound-effect cues |
| `index.html`, `compositions/` | The editable HyperFrames project (generated from `src/` by `tools/build.py`) |

## Preview, edit, render

```bash
npm install -g hyperframes@0.8.209        # or use npx as below
npx hyperframes preview                   # Studio preview in the browser
npx hyperframes check                     # lint, layout, contrast, audio checks
npx hyperframes render -q delivery --fps 30 -o ai_automations_sri_final.mp4
```

**Changing copy, colours or the CTA keyword:** edit `project.config.json`, then run `python3 tools/build.py` and `npx hyperframes check`. Change scene layouts and animations in `src/scenes/*.html`, never in `compositions/`, which is regenerated on every build. Inside each scene, `W.<word>` is the scene-local time of that spoken word, so animations stay locked to the voice.

The HyperFrames desktop app is a nicer way to keep editing visually: <https://hyperframes.dev/studio/download>.

## How it was made (all local, offline)

| Step | Tool | Script |
| --- | --- | --- |
| Voiceover | Kokoro-82M, voice `hm_omega` (Indian English male), one clip per scene at 1.1× speed | `tools/make_vo.py` (needs `pip install kokoro-onnx soundfile`) |
| Word timings | Parakeet TDT 0.6B via `npx hyperframes transcribe --engine parakeet`, aligned to the script's exact wording | `tools/analyze_voice.py` |
| Captions and mouth shapes | Caption groups of 2–5 words; six mouth shapes per frame from the audio | `tools/analyze_voice.py` → `tools/timing.json`, `captions.srt` |
| Presenter | Original pixel-art sprite drawn in code (body, head, 3 eye states, 2 brow states, 6 mouths), 10× nearest-neighbour | `tools/make_sprite.py` |
| Music | MusicGen-small (Meta, run locally): original 110 BPM electronic bed, looped on bar lines | `tools/gen_music.py`, `tools/make_music.py` |
| Ducking | Music dips 9 dB under speech (60 ms attack, 350 ms release) | `tools/mix.py` |
| Sound effects | 11 effects from the HyperFrames bundle, Pixabay Content License (`assets/audio/sfx/CREDITS.md`) | cues in `project.config.json` |

Full rebuild after a script change:

```bash
cd tools && python3 make_vo.py && cd ..                      # writes voiceover.wav + vo_scenes.json in tools/
cp tools/voiceover.wav assets/audio/voiceover.wav
npx hyperframes transcribe assets/audio/voiceover.wav --engine parakeet --json   # writes transcript.json
cp transcript.json tools/words_raw.json
python3 tools/analyze_voice.py && python3 tools/mix.py && python3 tools/build.py && python3 tools/write_storyboard.py
```

## Measured, not heard

The audio was checked with meters, not by ear:

- Integrated loudness is −17.0 LUFS, with a true peak of −1.5 dBTP.
- The voice sits around −18 dB. The music sits around −26 dB in the gaps and about 9 dB lower under speech.

Listen once before you publish.

## Known limitations

- **Lip sync is audio-driven, not phoneme-accurate.** Each frame picks one of six mouth shapes (rest, pressed, small, open, wide, round) from the voice's loudness and spectrum, and the mouth closes between words. It follows the speech rhythm closely but is not true viseme alignment.
- **Length.** The video runs 54 s rather than about 45 s. The script takes 49 s at a natural pace, and the call-to-action frame is held for 12 s so viewers have time to follow and comment.
- **Illustrative examples.** All names, emails, invoice values and order numbers on the UI cards (Priya, Rahul, Northline Supplies, ₹48,200 and so on) are made up for illustration. The video shows no statistics or results.
