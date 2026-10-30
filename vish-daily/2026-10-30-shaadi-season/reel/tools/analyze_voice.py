"""Derives every timing in the film from the real voiceover.

Usage: python3 tools/analyze_voice.py
Reads  tools/script.json, tools/vo_scenes.json, tools/words_raw.json (Parakeet transcript of
       assets/audio/voiceover.wav) and the voiceover itself.
Writes tools/timing.json: script-spelled words with times, caption groups, per-frame mouth
       shapes (visemes) and per-scene windows; plus captions.srt at the project root.
"""
import json, re, difflib, os
import numpy as np, soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = lambda *p: os.path.join(ROOT, *p)
FPS = 30

script = json.load(open(T("tools", "script.json")))
scenes = json.load(open(T("tools", "vo_scenes.json")))
raw = json.load(open(T("tools", "words_raw.json")))
vo, sr = sf.read(T("assets", "audio", "voiceover.wav"))
if vo.ndim > 1:
    vo = vo.mean(1)

NUM = {"1": "one", "2": "two", "3": "three", "4": "four", "for": "four", "inquiries": "enquiries", "inquiry": "enquiry", "shadika": "shaadi", "agaya": "aa", "or": "aur", "apka": "aapka", "vats": "whatsapp", "do": "200", "mehandi": "mehendi", "sangit": "sangeet", "bharat": "baraat", "abgay": "aapka", "abge": "aapka", "whats": "whatsapp", "enquires": "enquiries"}


def norm(w):
    w = re.sub(r"[^a-z0-9']", "", w.lower())
    return NUM.get(w, w)


# ---------------------------------------------------------------- align script words to the transcript
words = []          # script tokens (as captioned), with the scene they belong to
for s in script:
    for tok in s["text"].split():
        words.append({"text": tok, "scene": s["id"], "parts": [norm(p) for p in tok.split("-") if norm(p)]})
flat, owner = [], []
for i, w in enumerate(words):
    for p in w["parts"]:
        flat.append(p); owner.append(i)
tx = [norm(x["text"]) for x in raw]
sm = difflib.SequenceMatcher(a=flat, b=tx, autojunk=False)
times = [None] * len(flat)
for tag, a0, a1, b0, b1 in sm.get_opcodes():
    if tag in ("equal", "replace"):
        for k in range(a1 - a0):
            j = b0 + min(k, b1 - b0 - 1)
            times[a0 + k] = (raw[j]["start"], raw[j]["end"])
matched = sum(t is not None for t in times)
for w in words:
    w["start"] = w["end"] = None
for k, t in enumerate(times):
    if t is None:
        continue
    w = words[owner[k]]
    w["start"] = t[0] if w["start"] is None else min(w["start"], t[0])
    w["end"] = t[1] if w["end"] is None else max(w["end"], t[1])
# interpolate any word the transcript missed
for i, w in enumerate(words):
    if w["start"] is None:
        prev = next((words[j]["end"] for j in range(i - 1, -1, -1) if words[j]["end"] is not None), 0)
        nxt = next((words[j]["start"] for j in range(i + 1, len(words)) if words[j]["start"] is not None), prev + 0.4)
        w["start"], w["end"] = prev, max(prev + 0.1, nxt - 0.02)
# the first word of each scene starts when its clip starts (Parakeet places a file's first word at 0)
sc_by = {s["id"]: s for s in scenes}
seen = set()
for w in words:
    if w["scene"] not in seen:
        seen.add(w["scene"]); w["start"] = max(w["start"], sc_by[w["scene"]]["vo_start"])
        w["end"] = max(w["end"], w["start"] + 0.12)
for w in words:
    del w["parts"]; w["start"] = round(w["start"], 3); w["end"] = round(w["end"], 3)
print(f"aligned {matched}/{len(flat)} sub-tokens from {len(raw)} transcript words")

# ---------------------------------------------------------------- caption groups (2–5 words)
KEY = {"shaadi", "season", "whatsapp?", "200", "unread", "late,", "next", "agent", "connected", "workflows.", "packages", "dates.", "approve", "reminders,", "time.", "vendor", "updated,", "workflow", "follow"}
FUNC = {"in", "to", "the", "a", "and", "your", "when", "of", "for", "into", "can", "keep", "let"}
groups, cur = [], []
for i, w in enumerate(words):
    cur.append(w)
    nxt = words[i + 1] if i + 1 < len(words) else None
    end_sent = w["text"][-1] in ".?!:"
    comma = w["text"].endswith(",")
    pause = nxt is not None and nxt["start"] - w["end"] >= 0.15
    newscene = nxt is not None and nxt["scene"] != w["scene"]
    if nxt is None or newscene or end_sent or (comma and len(cur) >= 2) or len(cur) >= 5 or (pause and len(cur) >= 3 and not (nxt is not None and nxt["text"].endswith(",") and len(cur) < 5)) or (nxt is not None and norm(nxt["text"]) == "and" and len(cur) >= 3):
        # never end a group on a small word: carry it into the next group
        carry = []
        while len(cur) > 2 and (norm(cur[-1]["text"]) in FUNC or cur[-1]["text"].lower().strip(".,") in FUNC) and not (nxt is None or newscene or end_sent):
            carry.insert(0, cur.pop())
        groups.append(cur); cur = carry
if cur:
    groups.append(cur)
cap = []
for gi, g in enumerate(groups):
    prev_end = groups[gi - 1][-1]["end"] if gi else 0
    start = max(g[0]["start"] - 0.06, prev_end + 0.01)
    end = g[-1]["end"] + 0.3
    if gi + 1 < len(groups):
        end = min(end, max(groups[gi + 1][0]["start"] - 0.06, g[-1]["end"]))
    cap.append({"id": f"cap{gi:02d}", "scene": g[0]["scene"], "start": round(start, 3), "end": round(end, 3),
                "words": [{"text": w["text"], "start": w["start"], "end": w["end"],
                           "key": norm(w["text"]) in {norm(k) for k in KEY}} for w in g]})
for a_, b_ in zip(cap, cap[1:]):
    b_["start"] = round(max(b_["start"], a_["end"]), 3)


def srt_time(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


with open(T("captions.srt"), "w") as f:
    for i, c in enumerate(cap, 1):
        f.write(f"{i}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n{' '.join(w['text'] for w in c['words'])}\n\n")

# ---------------------------------------------------------------- visemes from the audio
# Per frame: loudness opens the mouth; the spectrum picks the shape (bright hiss → E, dark → O).
hop = sr // FPS; nfr = int(len(vo) / sr * FPS) + 1
win = int(0.045 * sr)
rms, cen, hi = np.zeros(nfr), np.zeros(nfr), np.zeros(nfr)
freqs = np.fft.rfftfreq(win, 1 / sr); hann = np.hanning(win)
for f in range(nfr):
    c = f * hop; seg = vo[max(0, c - win // 2): c + win // 2]
    if len(seg) < win:
        seg = np.pad(seg, (0, win - len(seg)))
    rms[f] = np.sqrt(np.mean(seg ** 2))
    sp = np.abs(np.fft.rfft(seg * hann)) ** 2 + 1e-12
    cen[f] = (sp * freqs).sum() / sp.sum()
    hi[f] = sp[freqs > 3000].sum() / sp[(freqs > 150) & (freqs < 1200)].sum()
voiced_ref = np.percentile(rms[rms > 0.01], 92) if (rms > 0.01).any() else 1
lvl = np.clip(rms / voiced_ref, 0, 1.2)
speaking = np.zeros(nfr, bool)
for w in words:
    speaking[int(w["start"] * FPS): int(w["end"] * FPS) + 2] = True
# thresholds come from this voice's own spectrum, not fixed numbers
sp_idx = speaking & (lvl > 0.22)
c_lo, c_hi = np.percentile(cen[sp_idx], [22, 80]); h_hi = np.percentile(hi[sp_idx], 82)
print(f"centroid p22={c_lo:.0f}Hz p80={c_hi:.0f}Hz, hiss p82={h_hi:.2f}")
vis = []
for f in range(nfr):
    if not speaking[f] or lvl[f] < 0.1:
        v = "rest"
    elif lvl[f] < 0.22:
        v = "M"
    elif hi[f] >= h_hi and lvl[f] < 0.8:
        v = "E"
    elif cen[f] <= c_lo:
        v = "O"
    elif lvl[f] > 0.62 or cen[f] >= c_hi:
        v = "A"
    else:
        v = "B"
    vis.append(v)
# hold every shape for at least two frames so it never flickers
for f in range(1, nfr - 1):
    if vis[f] != vis[f - 1] and vis[f] != vis[f + 1]:
        vis[f] = vis[f - 1]
code = {"rest": "r", "M": "m", "B": "b", "A": "a", "E": "e", "O": "o"}
counts = {k: vis.count(k) for k in code}
print("viseme frames:", counts)

json.dump({"fps": FPS, "vo_duration": round(len(vo) / sr, 3), "scenes": scenes, "words": words, "captions": cap,
           "visemes": "".join(code[v] for v in vis)}, open(T("tools", "timing.json"), "w"), indent=1)
print(len(cap), "caption groups;", "words:", len(words))
for c in cap:
    print(f"{c['start']:6.2f}-{c['end']:6.2f} {' '.join(w['text'] for w in c['words'])}")
