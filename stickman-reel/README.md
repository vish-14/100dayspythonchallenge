# "Waiting for the Perfect Time" — stickman comedy reel

1080×1920, 34 s, loopable. Built with [HyperFrames](https://hyperframes.heygen.com). All voices, music and sound effects are generated offline in code. No outside audio is used.

**Rendered video:** [`stickman-reel.mp4`](stickman-reel.mp4)

The spoken script needs about 20 s of talk on its own, so the reel runs 34 s instead of 20 s. Every line is kept word for word and the scenes stay in the original order. Each beat lasts as long as its line needs. Start times are in `src/timeline.json` (`beats`, `lines`, `sfx`, `music`).

## How it's made

| Step | File | What it does |
| --- | --- | --- |
| Voices | `src/make_voices.py` | Kokoro-82M (offline, open source) through `hyperframes tts`, with each character shaped by speed and an ffmpeg `rubberband` pitch shift |
| Soundtrack | `src/make_audio.py` | Original music: C major ukulele-style plucks at 115 BPM → A minor piano at 80 BPM → record scratch → 140 BPM kick/clap/bright lead → C major resolve that leads back into bar 1. Also synthesizes every SFX, places voices at their bubble times, ducks the music 60% under speech, and writes per-character mouth envelopes (30 fps) |
| Composition | `src/template.html` → `index.html` | SVG stickmen with posable joints, lip-synced mouths and speech-bubble subtitles. `src/build_stick.py` injects the timeline and mouth data |

Voices: Stickman (Michael; lazy until "Okay. Let's go.", then faster and higher), Investor (Adam −5 st, slow), Mentor (George −2 st), Motivation (Sky +6 st, fast), Ant (Michael +10 st, very fast), Customers (Adam/Heart/George/Nova, overlapping, different pitches).

## Rebuild

```bash
pip install kokoro-onnx soundfile numpy
cd src
python3 make_voices.py <hyperframes-project-dir> voices
python3 make_audio.py timeline.json voices ../assets/stickman-sound.wav mouths.json
python3 build_stick.py .. template.html   # writes ../index.html with the timeline and mouth data
cd .. && npm run check && npm run render
```
