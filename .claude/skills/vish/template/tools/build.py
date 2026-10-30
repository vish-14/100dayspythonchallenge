"""Assembles the HyperFrames project from project.config.json + tools/timing.json.

Usage: python3 tools/build.py

Writes index.html (scene hosts, presenter, captions, audio) and compositions/*.html from the
templates in src/. Template tokens:
  {{BASE_CSS}} {{CHROME}} {{W}} {{DUR}} {{ID}}       shared CSS, chrome labels, word cues (scene-local seconds), length, id
  {{c.path.to.value}}                                 this scene's copy from config.copy.<scene>
  {{brand.x}} {{colors.x}}                            config lookups
Every timing comes from the real voiceover: a scene starts 0.15 s before its first word.
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *p: os.path.join(ROOT, *p)
CFG = json.load(open(P("project.config.json")))
TIM = json.load(open(P("tools", "timing.json")))
VW, VH, DUR = CFG["video"]["width"], CFG["video"]["height"], CFG["video"]["duration"]
COL = CFG["colors"]


def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower()).replace("'", "")


# ---------------------------------------------------------------- scene windows
vo = {s["id"]: s for s in TIM["scenes"]}
order = [s["id"] for s in CFG["scenes"]]
starts = {sid: (0.0 if i == 0 else round(vo[sid]["vo_start"] - 0.15, 3)) for i, sid in enumerate(order)}
win = {}
for i, sid in enumerate(order):
    end = starts[order[i + 1]] if i + 1 < len(order) else DUR
    win[sid] = (starts[sid], round(end, 3))


def word_cues(sid):
    s0 = win[sid][0]; cues = {}; seen = {}
    for w in TIM["words"]:
        if w["scene"] != sid:
            continue
        k = norm(w["text"]); seen[k] = seen.get(k, 0) + 1
        key = k if seen[k] == 1 else f"{k}_{seen[k]}"
        cues[key] = round(w["start"] - s0, 3)
        cues[key + "_end"] = round(w["end"] - s0, 3)
    return cues


def abs_word(ref):
    """'scene:Word' → absolute start of that word; 'scene:word_2' → its second occurrence."""
    sid, txt = ref.split(":", 1)
    n = 1
    m = re.match(r"(.+)_(\d+)$", txt)
    if m:
        txt, n = m.group(1), int(m.group(2))
    hits = [w for w in TIM["words"] if w["scene"] == sid and (w["text"] == txt or norm(w["text"]) == norm(txt))]
    if len(hits) < n:
        raise KeyError(ref)
    return hits[n - 1]["start"]


# ---------------------------------------------------------------- shared CSS / chrome
def css_vars():
    return ";".join(f"--{k.replace('_', '-')}:{v}" for k, v in COL.items())


BASE_CSS = """
#root{position:absolute;inset:0;overflow:hidden;font-family:'Inter',sans-serif;%VARS%}
.panel{position:absolute;left:0;top:0;width:1080px;height:1010px}
.full{position:absolute;left:0;top:0;width:1080px;height:1920px}
.bg-dark{background:var(--ink)} .bg-blue{background:var(--blue)}
.mono{font-family:'JetBrains Mono',monospace;letter-spacing:.3em;text-transform:uppercase;font-weight:500}
.disp{font-family:'Montserrat',sans-serif;font-weight:900;letter-spacing:-.02em;line-height:.92}
.chrome{position:absolute;left:56px;right:56px;display:flex;justify-content:space-between;align-items:center;font-size:24px}
.chrome.top{top:200px}.chrome.bot{top:900px}
.prog{width:220px;height:3px;position:relative}
.prog i{position:absolute;left:0;top:0;height:3px;width:220px;transform-origin:0 50%}
.t-dark{color:var(--gray)} .t-dark .prog{background:var(--gray-line)} .t-dark .prog i{background:var(--paper)}
.t-blue{color:rgba(245,245,247,.86)} .t-blue .prog{background:rgba(245,245,247,.3)} .t-blue .prog i{background:var(--paper)}
.card{position:absolute;background:var(--paper);color:var(--ink);border-radius:22px;box-shadow:0 28px 60px rgba(4,8,20,.38);overflow:hidden}
.card .bar{height:58px;border-bottom:2px solid #E1E4EA;display:flex;align-items:center;gap:10px;padding:0 24px;font-family:'JetBrains Mono',monospace;font-size:20px;letter-spacing:.16em;color:#4E5666;text-transform:uppercase;font-weight:500}
.dot{width:12px;height:12px;border-radius:50%;background:#C6CBD5}.dot.b{background:var(--blue)}
.ln{height:14px;border-radius:7px;background:#DADDE4}
.tag{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:20px;letter-spacing:.16em;font-weight:500;padding:8px 14px;border-radius:10px;text-transform:uppercase}
.tag.blue{background:var(--blue);color:#fff}.tag.ink{background:var(--ink);color:#fff}.tag.ghost{border:2px solid currentColor}
.mask{overflow:hidden;display:block}
.head{position:absolute;left:56px;top:262px;display:flex;align-items:flex-start;gap:26px}
.head .num{font-size:150px;color:var(--blue)}
.head .ttl{font-size:66px;line-height:.98;padding-top:12px}
.t-blue .head .num, .on-blue .num{color:var(--paper)}
"""


def chrome(sc, s0, s1, top_only=False):
    th = "t-blue" if sc["theme"] == "blue" else "t-dark"
    p0, p1 = s0 / DUR, s1 / DUR
    top = (f'<div id="{sc["id"]}-chrome-top" class="chrome top mono {th}"><span>{html.escape(CFG["brand"]["series_label"])}</span>'
           f'<span>{html.escape(sc["counter"])}</span></div>')
    if top_only:
        return top, p0, p1
    bot = (f'<div id="{sc["id"]}-chrome-bot" class="chrome bot mono {th}"><span>{html.escape(sc["chapter"])}</span>'
           f'<span class="prog"><i id="{sc["id"]}-prog"></i></span></div>')
    return top + bot, p0, p1


def lookup(path, scope):
    cur = scope
    for part in path.split("."):
        cur = cur[int(part)] if isinstance(cur, list) else cur[part]
    return cur


def render_template(src, sc):
    sid = sc["id"]; s0, s1 = win[sid]
    ch, p0, p1 = chrome(sc, s0, s1, top_only=sc["layout"] == "takeover")
    out = src.replace("{{BASE_CSS}}", BASE_CSS.replace("%VARS%", css_vars()))
    out = out.replace("{{CHROME}}", ch).replace("{{P0}}", f"{p0:.4f}").replace("{{P1}}", f"{p1:.4f}")
    out = out.replace("{{W}}", json.dumps(word_cues(sid))).replace("{{DUR}}", f"{s1 - s0:.3f}").replace("{{ID}}", sid)
    scope = {"c": CFG["copy"].get(sid, {}), "brand": CFG["brand"], "colors": COL}
    out = re.sub(r"\{\{((?:c|brand|colors)\.[\w.]+)\}\}", lambda m: html.escape(str(lookup(m.group(1), scope))), out)
    assert "{{" not in out, re.findall(r"\{\{[^}]*\}\}", out)[:5]
    return out


# ---------------------------------------------------------------- scenes
os.makedirs(P("compositions"), exist_ok=True)
for sc in CFG["scenes"]:
    src = open(P("src", "scenes", sc["id"] + ".html")).read()
    open(P("compositions", sc["id"] + ".html"), "w").write(render_template(src, sc))

# ---------------------------------------------------------------- presenter
FPS = TIM["fps"]
vis = TIM["visemes"]
pres_in = abs_word("hook:while") - 0.02
pres_out = win["key"][0]
# blinks: every ~2.6–4 s, skipping moments the presenter is off screen
blinks, t, k = [], pres_in + 1.1, 0
while t < pres_out - 0.4:
    blinks.append(round(t, 3)); k += 1; t += (2.7, 3.6, 3.1, 4.0, 2.9)[k % 5]
# brows lift on the numbered headlines and the hook
brow_up = [round(abs_word(r), 3) for r in ("hook:cold", "problem:already", "solution:built", "a1:First,", "a2:Second,", "a3:Third,", "a4:Fourth,")]
# restrained head moves in whole sprite pixels (10 px): one small shift per scene, back to centre at the next
moves = [(round(win[s][0] + 0.2, 3), dx, dy) for s, dx, dy in (("problem", -10, 0), ("solution", 0, 0), ("a1", 10, 0), ("a2", 0, 0), ("a3", 0, 10), ("a4", -10, 0))]
moves.append((round(abs_word("a1:style.") + 0.1, 3), 0, -10))
moves.sort()
# hook mode (optional): a cut-out presenter during the hook, with props, hard-cut jumps and an optional dance.
# "anchor_hook": true  -> news desk + mic + plate, cuts on the breaking-news words
# "hook_mode": {"props": ["#pp-turban"], "cuts": [[time or "scene:word", offset, x, scale], ...], "dance": true}
#   "dance" may also be {"t0": time or "scene:word", "period": s} to bounce (and strike the dhol sticks) on the music's beat
hook_cuts, hook_end, hook_props, dance = [], 0, [], None
def _w(r, d=0.0):
    try: return round((r if isinstance(r, (int, float)) else abs_word(r)) + d, 3)
    except KeyError: return None
if CFG.get("anchor_hook"):
    raw = [(0.0, -170, 0.84), (0.35, 190, 0.9), (0.70, 0, 1.06), (_w("hook:Breaking", -0.04), 0, 1.0),
           (_w("hook:Aaj", -0.05), -160, 0.9), (_w("hook:ek", -0.05), 170, 0.92), (_w("hook:haath", -0.05), 0, 1.1)]
    hook_cuts = [list(c) for c in raw if c[0] is not None]
    hook_end, hook_props = win["problem"][0], ["#pp-desk", "#pp-mic", "#pp-plate"]
elif CFG.get("hook_mode"):
    hm = CFG["hook_mode"]
    hook_cuts = [[_w(r, d), x, s] for r, d, x, s in hm.get("cuts", []) if _w(r, d) is not None]
    hook_end, hook_props = win["problem"][0], hm.get("props", [])
    dv = hm.get("dance")
    if isinstance(dv, dict): dance = [_w(dv.get("t0", 0.0)) or 0.0, float(dv.get("period", 0.3))]
    elif dv: dance = [0.0, 0.3]
src = open(P("src", "presenter.html")).read()
pres = (src.replace("{{BASE_CSS}}", BASE_CSS.replace("%VARS%", css_vars()))
        .replace("{{VISEMES}}", json.dumps(vis)).replace("{{FPS}}", str(FPS))
        .replace("{{BLINKS}}", json.dumps(blinks)).replace("{{BROWS}}", json.dumps(brow_up))
        .replace("{{MOVES}}", json.dumps(moves)).replace("{{IN}}", f"{pres_in:.3f}").replace("{{OUT}}", f"{pres_out:.3f}")
        .replace("{{DUR}}", f"{DUR:.3f}").replace("{{HOOK_END}}", f"{hook_end:.3f}").replace("{{CUTS}}", json.dumps(hook_cuts)).replace("{{HOOK_PROPS}}", json.dumps(hook_props)).replace("{{DANCE}}", json.dumps(dance))
        .replace("{{PLATE}}", html.escape(CFG.get("anchor_plate", "VISH · LIVE"))))
open(P("compositions", "presenter.html"), "w").write(pres)

# ---------------------------------------------------------------- captions
caps = TIM["captions"]
groups_html, tweens = [], []
for c in caps:
    txt = " ".join(w["text"] for w in c["words"])
    fs = int(min(52, 900 / (0.64 * max(8, len(txt)))))
    words = " ".join(f'<span class="w{" key" if w["key"] else ""}">{html.escape(w["text"])}</span>' for w in c["words"])
    d = round(c["end"] - c["start"], 3)
    groups_html.append(f'<div id="{c["id"]}" class="clip cap" data-start="{c["start"]:.3f}" data-duration="{d:.3f}" data-track-index="0">'
                       f'<span class="strip" style="font-size:{fs}px">{words}</span></div>')
    tweens.append((c["id"], c["start"], c["end"]))
cap_html = f"""<template>
  <style>
    #root{{position:absolute;inset:0;pointer-events:none}}
    .cap{{position:absolute;left:0;top:962px;width:1080px;height:96px;display:flex;align-items:center;justify-content:center;overflow:visible}}
    .cap .strip{{display:inline-block;background:{COL["paper"]};color:{COL["ink"]};font-family:'Montserrat',sans-serif;font-weight:800;
      line-height:1.05;padding:14px 30px 16px;letter-spacing:-.005em;box-shadow:0 10px 30px rgba(4,8,20,.28);white-space:nowrap}}
    .cap .key{{color:{COL["blue"]}}}
  </style>
  <div id="root" data-composition-id="captions" data-width="{VW}" data-height="{VH}">
    {"".join(groups_html)}
  </div>
  <script>
    (() => {{
      const tl = gsap.timeline({{ paused: true }});
      const G = {json.dumps(tweens)};
      G.forEach(([id, s, e]) => {{
        const strip = document.querySelector("#" + id + " .strip");
        tl.fromTo(strip, {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.12, ease: "power3.out" }}, s);
        tl.to(strip, {{ opacity: 0, duration: 0.08, ease: "power2.in" }}, Math.max(s + 0.14, e - 0.08));
        tl.set(strip, {{ opacity: 0 }}, e);
      }});
      window.__timelines["captions"] = tl;
    }})();
  </script>
</template>
"""
open(P("compositions", "captions.html"), "w").write(cap_html)

# ---------------------------------------------------------------- root
hosts = []
for i, sc in enumerate(CFG["scenes"]):
    s0, s1 = win[sc["id"]]
    hosts.append(f'<div id="{sc["id"]}" data-composition-id="{sc["id"]}" data-composition-src="compositions/{sc["id"]}.html" '
                 f'data-start="{s0:.3f}" data-duration="{s1 - s0:.3f}" data-track-index="1" data-track-kind="graphics" '
                 f'data-width="{VW}" data-height="{VH}" style="z-index:{2}"></div>')
# each effect gets its real length and the first free lane, so no two overlap on one track
man = json.load(open(P(CFG["assets"]["sfx_dir"], "manifest.json")))
lanes, sfx = [], []
for i, s in enumerate(sorted(CFG["sfx"], key=lambda s: abs_word(s["word"]) + s.get("offset", 0))):
    t = max(0.0, abs_word(s["word"]) + s.get("offset", 0))
    d = man[s["file"].rsplit(".", 1)[0]]["duration"]
    lane = next((k for k, end in enumerate(lanes) if end <= t), None)
    if lane is None:
        lanes.append(0); lane = len(lanes) - 1
    lanes[lane] = t + d
    sfx.append(f'<audio id="sfx{i:02d}" src="{CFG["assets"]["sfx_dir"]}/{s["file"]}" data-start="{t:.3f}" data-duration="{d}" '
               f'data-volume="{s["volume"]}" data-track-index="{10 + lane}"></audio>')
a = CFG["assets"]
root_html = f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={VW}, height={VH}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {VW}px; height: {VH}px; overflow: hidden; background: {COL["ink"]}; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
      #bg {{ position: absolute; inset: 0; background: {COL["ink"]}; }}
    </style>
  </head>
  <body>
    <!-- Generated by tools/build.py from project.config.json and tools/timing.json. Edit those, then rebuild. -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{VW}" data-height="{VH}">
      <div id="bg"></div>
      {chr(10).join("      " + h for h in hosts).strip()}
      <div id="presenter" data-composition-id="presenter" data-composition-src="compositions/presenter.html" data-start="0" data-duration="{DUR}" data-track-index="2" data-track-kind="graphics" data-width="{VW}" data-height="{VH}" style="z-index:3"></div>
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{DUR}" data-track-index="3" data-track-kind="captions" data-width="{VW}" data-height="{VH}" style="z-index:6"></div>
      <audio id="voiceover" src="{a["voiceover"]}" data-start="0" data-volume="{CFG["audio"]["voice_volume"]}" data-track-index="4"></audio>
      <audio id="music" src="{a["music_bed"]}" data-start="0" data-volume="{CFG["audio"]["music_volume"]}" data-track-index="8"></audio>
      {chr(10).join("      " + s for s in sfx).strip()}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
open(P("index.html"), "w").write(root_html)
json.dump({k: {"start": v[0], "end": v[1]} for k, v in win.items()}, open(P("tools", "scene_windows.json"), "w"), indent=1)
print("built:", ", ".join(f"{k} {v[0]:.2f}-{v[1]:.2f}" for k, v in win.items()))
