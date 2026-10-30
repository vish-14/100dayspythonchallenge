"""Writes STORYBOARD.md: the timestamped script and storyboard, from the real voiceover timings."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *p: os.path.join(ROOT, *p)
cfg = json.load(open(P("project.config.json"))); tim = json.load(open(P("tools", "timing.json")))
win = json.load(open(P("tools", "scene_windows.json"))); script = {s["id"]: s for s in json.load(open(P("tools", "script.json")))}
VIS = {
 "hook": "Vish on air from frame 0. Marigold frame SHAADI / SEASON! with swinging garlands, punching on each dhol hit, AA GAYA! stamp; cut to AUR AAPKA / WHATSAPP?; cut to a phone flooding with family messages, unread counter racing to 200, UNREAD / ENQUIRIES!, shake, flash out.",
 "problem": "Blue. WhatsApp list of four families, each asking for one thing (date, package, price, reply today); 2 DAYS LATER tag on \"reply late\"; BOOKED ELSEWHERE stamp on \"book the next planner\".",
 "solution": "Light panel: MY AI AGENT · FOR WEDDING BUSINESSES, nodes REPLY / QUOTE / PAYMENTS / VENDORS.",
 "a1": "Dark. 01 INSTANT REPLY: the Sharma family asks about 14 Dec, the AI replies with packages and open dates.",
 "a2": "Blue. 02 DRAFT QUOTE: AI draft types itself, cursor clicks Approve on \"approve\", Sent to Sharma family on \"out\".",
 "a3": "Dark. 03 PAYMENT REMINDERS: polite WhatsApp reminder, advance status flips Due -> Paid on \"come in\".",
 "a4": "Blue. 04 VENDOR UPDATES: vendor group for the Sharma wedding, a tick per vendor through caterer and decorator.",
 "cta": "Standard CTA (unchanged).",
}
sfx = {}
for s in cfg["sfx"]:
    sc, w = s["word"].split(":", 1); sfx.setdefault(sc, []).append(f'{s["file"].rsplit(".",1)[0]} on “{w.strip(".,:?")}”')
lines = ["# AI automations reel — timestamped script and storyboard", "",
         f"1080 × 1920, {cfg['video']['fps']} fps, {cfg['video']['duration']:.0f} s. Every time below comes from the real voiceover (Kokoro `hm_omega`, transcribed with Parakeet).", ""]
for sc in cfg["scenes"]:
    sid = sc["id"]; a, b = win[sid]["start"], win[sid]["end"]
    words = [w for w in tim["words"] if w["scene"] == sid]
    lines += [f"## {a:05.2f}–{b:05.2f} s · {sc['chapter']} ({sc['layout']})", "",
              f"**Voiceover** ({words[0]['start']:.2f}–{words[-1]['end']:.2f} s): “{script[sid]['text']}”", "",
              f"**Visual:** {VIS[sid]}", "",
              f"**Sound:** music bed ducked −9 dB under the voice; " + ("; ".join(sfx.get(sid, [])) or "music only") + ".", "",
              "**Captions:** " + " · ".join(f"{c['start']:.2f} “{' '.join(w['text'] for w in c['words'])}”" for c in tim["captions"] if c["scene"] == sid), ""]
open(P("STORYBOARD.md"), "w").write("\n".join(lines))
print("ok")
