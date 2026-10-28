# Four everyday tasks. One AI agent.

A 50-second Instagram Reel (1080 × 1920, 30 fps) built with HyperFrames. One AI agent, connected to the inbox, CRM, documents and team chat, handles enquiries, follow-ups, document summaries and team updates. It works through connected tools and clear rules, and people approve what matters. The video ends with an invitation to contact Sri Trilinga Technologies.

| File | What it is |
| --- | --- |
| `ai_agent_four_tasks.mp4` | Final video: H.264 + AAC, 50.0 s, −16.5 LUFS |
| `ai_agent_four_tasks.srt` | Captions, 32 phrase-level cues timed from the voiceover |
| `SCRIPT.md` | Final script with timings and what appears on screen |
| `project.config.json`, `src/`, `tools/` | Editable source (same pipeline as `../ai-automations-reel`) |

The script lives in `tools/script.json`. The `say` field is what the voice reads. The `text` field is the caption; `|` marks a caption break. Rebuild with:
1. `tools/make_vo.py`
2. `npx hyperframes transcribe assets/audio/voiceover.wav --engine parakeet --json`, then copy `assets/audio/transcript.json` to `tools/words_raw.json`
3. `tools/analyze_voice.py` → `tools/mix.py` → `tools/build.py`
4. `npx hyperframes render -q delivery --fps 30 -o ai_agent_four_tasks.mp4`
