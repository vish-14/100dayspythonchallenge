"""Writes STORYBOARD.md: the timestamped script and storyboard, from the real voiceover timings."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *p: os.path.join(ROOT, *p)
cfg = json.load(open(P("project.config.json"))); tim = json.load(open(P("tools", "timing.json")))
win = json.load(open(P("tools", "scene_windows.json"))); script = {s["id"]: s for s in json.load(open(P("tools", "script.json")))}
VIS = {
 "hook": "Full-screen dark takeover: PROPERTY AGENTS · BROKERS, YOUR ENQUIRIES / GO COLD (cover frame); a new-enquiry card with an UNANSWERED timer counting up; on “while” Vish rises and the chips UNANSWERED + YOU · ON A SITE VISIT appear.",
 "problem": "Blue panel. A portal chat: the buyer's 9:04 PM enquiry lands, the clock flips to 8:30 AM on “next morning” and your reply appears; on “another broker” a card slides in (On a call with your buyer) and your reply greys out as Seen · no reply.",
 "solution": "Light panel (the turn). THE SOLUTION, then MY AI AGENT rises on “AI agent”, FOR PROPERTY AGENTS; four numbered nodes pop on “four”, links fill on “connected”, labels RESPOND / QUALIFY / ROUTE + BOOK / FOLLOW UP and a 4 CONNECTED WORKFLOWS pill on “workflows”; node 01 lights blue as the hand-off.",
 "a1": "Dark. 01 RESPOND TO ENQUIRIES. A portal enquiry card lands, name and source fly into the CRM (Saved ✓), then the AI reply writes itself and a bar flips Sending… → Sent ✓ 9:05 PM, with Style: yours.",
 "a2": "Blue. 02 QUALIFY BUYERS. An AI asks bar cycles budget → location → timeline → home loan, each answer filling its CRM field; HOT LEAD stamps on “loan”.",
 "a3": "Dark. 03 ROUTE + BOOK. Calendar appears on “book”; the WhatsApp AI-agent alert (Ananya R. · meets criteria) lands on “The agent” and pings on “alerts”; a cursor taps Approve on “approve”; the site visit slides into Sat 11:00 and Booked ✓ stamps on “calendar”.",
 "a4": "Blue. 04 FOLLOW UP. Day 2 / 7 / 14 track; Rohan K. tagged NOT READY YET; an AI check-in message goes out; on “new matching properties” the lead moves to Day 7 and a 3BHK match card lands; the tag flips to STILL INTERESTED ✓.",
 "key": "Full-screen dark: THE KEY? → nodes PORTALS, CRM, AI AGENT, CALENDAR pop as named and check on “connected”; rules IF new lead / IF hot; the AI agent node branches to a You approve card; CONNECTED TOOLS → CLEAR RULES → YOU APPROVE below the captions.",
 "cta": "Standard CTA (unchanged): follow, then comment WORKFLOW, DM from Vish, FOLLOW + COMMENT “WORKFLOW” pill.",
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
