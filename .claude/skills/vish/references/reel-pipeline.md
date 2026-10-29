# Making a new Vish reel

The `template/` folder is the working HyperFrames project behind the first reel ("4 boring tasks"). Copy it, change the script and copy, and run the pipeline. Everything runs locally and offline after the first model downloads.

## Format and look

- 1080 × 1920, 30 fps, H.264 + AAC. About 45–60 s is fine.
- **Split screen:** editorial motion graphics in the top panel (y 0–1010), Vish in the lower panel (y 1010–1920), with full-screen takeovers for the hook, one emphasis beat and the CTA.
- **Type:** Montserrat 800/900 for headlines, JetBrains Mono for small letter-spaced labels, Inter for UI text.
- **Colours:** electric blue #2257EF, near-black #0B1016, off-white #F5F5F7, grey #8A93A3.
- **Instagram safe zone:** all words between y 168 and 1330. Captions are off-white strips with bold dark text on the panel boundary (y ≈ 962–1058). Nothing important under the right-hand action rail.
- Change something visible every 1–2 s; land every reveal on the word that names it.

## Pipeline

```bash
cp -r template my-new-reel && cd my-new-reel
npm i -g hyperframes@0.8.209            # or use npx
pip install kokoro-onnx soundfile numpy torch transformers   # voice + music (torch is CPU fine)
npx hyperframes models install parakeet --json < /dev/null   # word timestamps

# 1. Script: one entry per scene in tools/script.json (hook, problem, solution, a1–a4, key, cta)
#    {"id","label","say" (what the voice reads; spell C R M etc.),"text" (captions),"speed" (1.0; CTA 1.1)}
# 2. Voice "Vish warm" (picked by the user from 6 samples, Oct 2026): 50/50 blend of Kokoro hm_omega + hm_psi, lang en-gb,
#    speed 0.9 (CTA 1.0), pitch −1 semitone (formants kept), clarity EQ + de-ess + compression. All in tools/make_vo.py; keep it identical every day.
cd tools && python3 make_vo.py && cp voiceover.wav ../assets/audio/voiceover.wav && rm voiceover.wav && cd ..
# 3. Real word timings from the actual audio
npx hyperframes transcribe assets/audio/voiceover.wav --engine parakeet --json   # → transcript.json
cp transcript.json tools/words_raw.json
python3 tools/analyze_voice.py        # aligns to the script spelling; captions.srt, mouth shapes, timing.json
# 4. Music: original bed from MusicGen (run once), loop to the video length, duck under the voice
python3 tools/gen_music.py assets/audio/source/music_seed.wav "subtle minimal electronic underscore for a modern tech explainer, soft pulsing synth bass, light hi-hats, warm pads, 110 bpm, no vocals" 7
python3 tools/make_music.py assets/audio/source/music_seed.wav <video_seconds> assets/audio/music.wav
python3 tools/mix.py                  # −9 dB duck under speech, 60 ms attack / 350 ms release
# 5. Build compositions from src/ + project.config.json, then check and look
python3 tools/build.py && python3 tools/write_storyboard.py
npx hyperframes check
npx hyperframes snapshot --at 1,5,10,20,30,45     # look at the frames
# 6. Render
npx hyperframes render -q delivery --fps 30 -o vish_reel.mp4
```

## Where things live

- `project.config.json`: video length, brand (handle, label), colours, fonts, all on-screen copy per scene, SFX cues (each tied to a spoken word, e.g. `"a1:CRM,"`).
- `src/scenes/*.html`: one template per scene. Inside, `W.<word>` is the scene-local time of a spoken word (repeats get `_2`, `_3`), so animations stay locked to the voice. Edit here, never in `compositions/` (regenerated on every build).
- `src/presenter.html`: Vish's panel, lip sync, blinks, brows, head shifts. Layers live in `assets/presenter/`; regenerate them with `scripts/make_sprite.py` from this skill.
- `src/scenes/cta.html`: the follow + comment WORKFLOW ending (avatar at `assets/brand/avatar.png`).

## Breaking-news hook (optional, for low-reach periods)

Used in the 29 Oct short cut after the first reel got little reach from outside the network. Copy `template/hooks/breaking-news-hook.html` over `src/scenes/hook.html`, set the hook layout to `takeover`, set `pres_in = 0.0` in `tools/build.py` and use the instant-placement presenter line from the 29 Oct `reel-short/src/presenter.html` and set `LEAD = 1.4` in `tools/make_vo.py`, so the sting and the siren play before the voice. Keep the hook layout `split`.
- **Seven hard-cut full-screen frames, never one busy picture:** red BREAKING (hit 1, 0.00 s) → black NEWS (hit 2, 0.35 s) → red/blue strobe alert (hit 3, 0.70 s, siren) → TV news desk with LIVE and the ticker (on "Breaking news") → each headline line alone (AAJ RAAT SE / EK BHI LEAD / HAATH SE NAHI JAYEGI!) → a flash cut into the problem. The frames sit in the top panel and **Vish anchors the bulletin from frame 0** (`pres_in = 0.0`; the presenter is placed instantly instead of rising). Frame 0 is the thumbnail people see before swiping, so it must be fully readable, with no white flash.
- **Every cut gets a zoom punch, a white flash and a shake;** the last line also gets an RGB glitch and an ice tint.
- **Sounds:** `news-sting` (three brass/boom hits) and `siren-police` (rising wail → fast high-low-high yelps → falling wail, horn tone and echo, ducks under the voice after 1.3 s), both at the start of the hook. Regenerate them with `scripts/make_news_sfx.py`, and check the shape with a spectrogram (`ffmpeg -lavfi showspectrumpic`), since we can't listen.
- **Say it like an Indian broker, not a translation:** "thandi nahi padegi" was a word-for-word translation of "go cold", and nobody says it. Use real idioms: "ek bhi lead haath se nahi jayegi", "lead haath se nikal gayi", "enquiry miss nahi hogi". Check every Hindi line with the question: would a Mumbai or Hyderabad broker say this out loud?
- **Hinglish voice:** write Hindi in Devanagari with `"lang": "hi"`; captions stay in Roman Hinglish. Kokoro's Hindi sounds robotic to Indian ears. For a natural accent use `scripts/make_hindi_vo.py` (Indic Parler-TTS, speaker Rohit, needs `HF_TOKEN`) or a phone recording, then set `"audio": "<file>"` on that scene in `tools/script.json`.
- **Keep the problem beat punchy too:** a red UNREAD tag, a whip-flip of the clock, a "LEAD LOST ✗" stamp with a thud, and a riser that crests on the solution reveal.

## Lessons learned (avoid repeating these)

- **Story flow (user feedback, Oct 2026):** the reel must go problem → solution → workflows → CTA. A `solution` scene ("That's why I built an AI agent solution for … with four connected workflows") sits between `problem` and `a1`, and each workflow starts "First, … / Second, …" and is explained right away. See `daily-run.md` Step 2.
- **The automation is the actor:** "Serious buyers alert you on WhatsApp" wrongly implied the buyers send the alert. Write "The agent alerts you on WhatsApp when a buyer meets your criteria", and label UI cards the same way ("WhatsApp · AI agent alert", "meets criteria").
- **Long-file transcription slips:** on a 70 s+ voiceover, Parakeet sometimes mishears words that are clear on their own ("matching" → "marching"). Before rewording, regenerate just that line and transcribe it alone. Reword only if it fails in isolation too.

- **Voice clarity (user feedback, Oct 2026):** hm_omega with `lang='en-us'` at 1.0× was hard to understand for Indian viewers. Use `lang='en-gb'` at 0.9× (CTA 1.0×). Check every voiceover with Parakeet: any real mishearing ("hot"→"heart", "portals"→"orals", a dropped "-ed") means reword the line, not just re-roll it.
- **Say it the Indian way:** for Indian industries use local terms, not US ones: "property agents/brokers" not "realtors", "site visit" not "viewing", "enquiry", "home loan", "possession date", portals like 99acres, MagicBricks, Housing.com. Ask: would an Indian owner say this word out loud?

- Kokoro mispronounces "Sri Trilinga"; spell it "Shree Trilinga" in `say` and verify with Parakeet. (The current reels don't speak the company name.)
- Parakeet puts a file's first word at 0 s; `analyze_voice.py` already clamps each scene's first word to its clip start.
- **Masked text reveals:** a mask container taller than its text shows slivers of hidden letters. Size masks exactly, or use opacity + y fades (as the CTA headline does).
- SFX `<audio>` need `data-duration`, and overlapping ones need separate tracks (`build.py` assigns lanes).
- Music from MusicGen comes out quiet. Target −16 to −17 LUFS integrated with a true peak of −1.5 dBTP or lower, voice around −18 dB, music around −26 dB in the gaps. Check with: `ffmpeg -i reel.mp4 -af ebur128=peak=true -f null -`.
- `npx hyperframes check` flags masked or transforming text as overflow or occlusion mid-animation. Confirm with real frames before "fixing".
- Always check the rendered MP4 frames (ffmpeg) before delivering. You can only measure the audio, not hear it, so say so.
