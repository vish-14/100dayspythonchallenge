# Four everyday tasks. One AI agent.

A 52-second Instagram Reel for @vish.workflows (1080 × 1920, 30 fps), built with HyperFrames. One AI agent, connected to the inbox, CRM, documents and team chat, handles enquiries, follow-ups, document summaries and team updates. It works through connected tools and clear rules, and people approve what matters. The video ends with the follow + comment "WORKFLOW" call to action, which triggers the SuperProfile auto-DM.

| File | What it is |
| --- | --- |
| `ai_agent_four_tasks.mp4` | Final video: H.264 + AAC, 52.2 s, −16.6 LUFS |
| `ai_agent_four_tasks.srt` | Captions, 35 phrase-level cues timed from the voiceover |
| `SCRIPT.md` | Final script with timings and what appears on screen |
| `project.config.json`, `src/`, `tools/` | Editable source (same pipeline as `../ai-automations-reel`) |

The script lives in `tools/script.json`. The `say` field is what the voice reads, and `speed` sets 1.1× for the call to action. The `text` field is the caption; `|` marks a caption break. Rebuild with:
1. `tools/make_vo.py`
2. `npx hyperframes transcribe assets/audio/voiceover.wav --engine parakeet --json`, then copy `assets/audio/transcript.json` to `tools/words_raw.json`
3. `tools/analyze_voice.py` → `tools/make_music.py` → `tools/mix.py` → `tools/build.py`
4. `npx hyperframes render -q delivery --fps 30 -o ai_agent_four_tasks.mp4`
