"""Builds and renders one hook variant of the 25-second reel.

Usage: python3 tools/make_variant.py h1|h2|h3
The agent scene and the call to action are shared; only the opening line (tools/variants.json) changes.
Writes reel_<id>.mp4 and reel_<id>.srt at the project root.
"""
import json, os, subprocess, sys, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
vid = sys.argv[1]
V = json.load(open("tools/variants.json"))[vid]
run = lambda *c, **k: subprocess.run(c, check=True, **k)

AGENT = ("Here's how one AI agent helps. It replies to enquiries, follows up on time, summarises documents, "
         "and keeps your team updated. You approve what matters.")
script = [
    {"id": "hook", "label": "HOOK", "say": V["say"], "text": V["say"]},
    {"id": "agent", "label": "AI AGENT", "say": AGENT,
     "text": "Here's how one AI agent helps. | It replies to enquiries, | follows up on time, | summarises documents, | "
             "and keeps your team updated. | You approve what matters."},
    {"id": "cta", "label": "YOUR TURN", "speed": 1.1,
     "say": "Want it built for your business? Follow me and comment, workflow. I'll send the details to your DMs.",
     "text": "Want it built | for your business? | Follow me | and comment “WORKFLOW”. | I'll send the details | to your DMs."},
]
json.dump(script, open("tools/script.json", "w"), indent=1, ensure_ascii=False)

# 1. voice, word timings, captions and mouth shapes
run("python3", "make_vo.py", cwd="tools")
shutil.move("tools/voiceover.wav", "assets/audio/voiceover.wav")
run("npx", "hyperframes", "transcribe", "assets/audio/voiceover.wav", "--engine", "parakeet", "--json",
    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
shutil.copy("assets/audio/transcript.json", "tools/words_raw.json")
run("python3", "tools/analyze_voice.py", stdout=subprocess.DEVNULL)
print("heard:", " ".join(w["text"] for w in json.load(open("tools/words_raw.json"))))

# 2. config for this variant: length = voice + about 1.8 s hold on the call to action
vo_end = json.load(open("tools/vo_scenes.json"))[-1]["vo_end"]
dur = round(vo_end + 1.8, 1)
c = json.load(open("project.config.json"))
c["video"]["duration"] = dur
c["copy"]["hook"]["text"] = V["text"]
c["presenter"]["brows"] = [V["brow"], "agent:approve"]
first = V["say"].split()[0]
c["sfx"] = [s for s in c["sfx"] if not s["word"].startswith("hook:")] + [
    {"file": "impact-bass-1.mp3", "word": f"hook:{first}", "offset": 0.0, "volume": 0.3}]
json.dump(c, open("project.config.json", "w"), indent=2, ensure_ascii=False)

# 3. music, mix, build, check, render
run("python3", "tools/make_music.py", "assets/audio/source/music_seed.wav", str(dur), "assets/audio/music.wav", stdout=subprocess.DEVNULL)
run("python3", "tools/mix.py", stdout=subprocess.DEVNULL)
run("python3", "tools/build.py")
if "--render" in sys.argv:
    run("npx", "hyperframes", "render", "-q", "delivery", "--fps", "30", "-o", f"reel_{vid}.mp4", stdout=subprocess.DEVNULL)
    shutil.copy("captions.srt", f"reel_{vid}.srt")
print(f"{vid}: {dur} s")
