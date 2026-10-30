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

## Festive / themed hook mode (cut-out Vish with props)

Set `"hook_mode"` in `project.config.json` to make Vish a cut-out (no blue panel) during the hook, wearing props and jumping on hard cuts, with his normal panel back at the problem:
`"hook_mode": {"props": ["#pp-turban"], "dance": true, "cuts": [[0.0, 0, 0, 1.0], ["hook:Aur", -0.04, -150, 0.9], ["hook:200", -0.12, 170, 0.88]]}` (each cut is a time or a "scene:word", an offset, an x shift and a scale). `"dance": true` adds a bounce and a head tilt on every 0.3 s beat ("balle balle"). Props: `#pp-turban` (wedding safa), or the news set `#pp-desk`, `#pp-mic`, `#pp-plate` (or simply `"anchor_hook": true`). The hook frames must then be full height (1920) so there is a scene behind him.
- **Wedding version (30 Oct, "Shaadi season"):** `template/hooks/wedding-hook.html`. A marigold frame with garlands, a blinking fairy-light string, six original bhangra silhouettes switching poses on the beat and falling marigold petals; then dark festive frames with bokeh lights. Sound: the original `dhol-intro` and a quiet `dhol-loop` under the voice (`scripts/make_dhol_sfx.py`), with `LEAD = 0.9` so the dhol lands before the voice.
- **Wedding v2 (30 Oct, after "dhol sounds fake, voice robotic, make it more Indian"):** the current `wedding-hook.html` has seven fast cuts: BALLE BALLE! (spinning sunburst, confetti, gold beat ring) → SHAADI SEASON AA GAYA! (marigolds, dancers, petals) → MEHENDI (henna draws itself on a palm, whip-in) → SANGEET (sweeping spotlights, disco ball, notes, whip-in) → BARAAT (fireworks, BAND BAAJA, crowd, whip-in) → AUR AAPKA WHATSAPP? → the 200-enquiry flood.
  - **Vish plays the dhol:** props `["#pp-turban", "#pp-dhol", "#pp-dagga", "#pp-tilli"]`. With the sticks in the props, `"dance": {"t0": <first beat s>, "period": <half beat s>}` makes the dagga and tilli strike alternately on the music's beat while he bounces.
  - **"Balle balle" is shown, not spoken** (user's call): the BALLE BALLE frame plays over the dhol for `LEAD = 1.5` s, and the voice starts at "Shaadi ka season aa gaya!".
  - **Mixed-language line:** Kokoro mangles English words written in Devanagari ("व्हाट्सऐप", "अनरेड"). Give the hook `"parts": [[text, lang, gap_s], ...]`: the Hindi in `hi`, and "WhatsApp?" and "Two hundred unread enquiries!" in `en-gb`, all in the same voice (`"voice": "hm_psi"`, the user's pick, at 0.95×). Parakeet then hears the English correctly. Hindi "pe?" on its own was misheard, so it became "Aur aapka WhatsApp?".
  - **Real dhol:** the synthesised dhol sounded fake. The user picked a MusicGen take: prompt "baraat band dhol and dhol tasha street wedding procession, loud acoustic drums, festive", seed 5, 500 tokens. Before syncing anything to it, measure its beat with onset autocorrelation (this take: 0.72 s, first hit 0.204 s).
    - **Cut it dead on "aur"** with a 0.12 s fade, so the party stops for the question. Bake in a −6 dB dip once the voice starts.
    - **Silence the music bed during the hook:** `"audio": {"music_from": "problem"}`.
    - **File:** `template/assets/audio/sfx/dhol-baraat.mp3`.
    - **Fallback:** `scripts/make_dhol_sfx.py` v2 (modal drum model).
  - **Other voices tried:** Bark (`suno/bark-small`, `v2/hi_speaker_N`, MIT) sounds more human but is slow on CPU (~2 min per line) and can slur. Installing `edge-tts` was blocked by the sandbox's permission check. Indic Parler-TTS needs `HF_TOKEN`.

## Breaking-news hook (optional, for low-reach periods)

Used in the 29 Oct short cut after the first reel got little reach from outside the network. The final version (v9) is the reference: `vish-daily/2026-10-29-speed-to-lead/reel-short/`.

- **Vish as the news anchor:** set `"anchor_hook": true` (and optionally `"anchor_plate": "VISH · LIVE"`) in `project.config.json`. During the hook he is a cut-out (no blue panel) behind a fixed news desk (`prop_desk`) with a mic (`prop_mic`), jumping position and size on every hard cut while the frames flash behind him. At the problem, his normal blue panel returns and the props go. The hook frames must then be full height (1920).
- **Siren layer over every cut, not just one frame:** police light bar, red/blue edge glow, a blinking LIVE badge and an alert ping on each headline cut.
- **Act out the key phrase:** on "haath se nahi jayega", hands hold a LEAD card, it slips, a red ✕ slams on, it snaps back and ✓ SECURED pops. Every frame gets a slow zoom drift, and "aaj raat se" gets a moon and a clock ticking to 11:00 PM, so nothing sits still. Copy `template/hooks/breaking-news-hook.html` over `src/scenes/hook.html`, set the hook layout to `takeover`, set `pres_in = 0.0` in `tools/build.py` and use the instant-placement presenter line from the 29 Oct `reel-short/src/presenter.html` and set `LEAD = 1.4` in `tools/make_vo.py`, so the sting and the siren play before the voice. Keep the hook layout `split`.
- **Seven hard-cut full-screen frames, never one busy picture:** red BREAKING (hit 1, 0.00 s) → black NEWS (hit 2, 0.35 s) → red/blue strobe alert (hit 3, 0.70 s, siren) → TV news desk with LIVE and the ticker (on "Breaking news") → each headline line alone (AAJ RAAT SE / EK BHI LEAD / HAATH SE NAHI JAYEGI!) → a flash cut into the problem. The frames sit in the top panel and **Vish anchors the bulletin from frame 0** (`pres_in = 0.0`; the presenter is placed instantly instead of rising). Frame 0 is the thumbnail people see before swiping, so it must be fully readable, with no white flash.
- **Every cut gets a zoom punch, a white flash and a shake;** the last line also gets an RGB glitch and an ice tint.
- **Sounds:** `news-sting` (three brass/boom hits) and `siren-police` (rising wail → fast high-low-high yelps → falling wail, horn tone and echo, ducks under the voice after 1.3 s), both at the start of the hook. Regenerate them with `scripts/make_news_sfx.py`, and check the shape with a spectrogram (`ffmpeg -lavfi showspectrumpic`), since we can't listen.
- **Say it like an Indian broker, not a translation:** "thandi nahi padegi" was a word-for-word translation of "go cold", and nobody says it. Use real idioms: "ek bhi lead, haath se nahi jayega!" (masculine: जाएगा; the comma also helps the voice), "lead haath se nikal gayi", "enquiry miss nahi hogi". Check every Hindi line with the question: would a Mumbai or Hyderabad broker say this out loud?
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
