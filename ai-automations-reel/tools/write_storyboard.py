"""Writes STORYBOARD.md: the timestamped script and storyboard, from the real voiceover timings."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *p: os.path.join(ROOT, *p)
cfg = json.load(open(P("project.config.json"))); tim = json.load(open(P("tools", "timing.json")))
win = json.load(open(P("tools", "scene_windows.json"))); script = {s["id"]: s for s in json.load(open(P("tools", "script.json")))}
VIS = {
 "hook": "Full-screen takeover: “4 B●RING” on screen from frame 0 (the O is an electric-blue circle); “TASKS” rises on “tasks”. On “One smarter workflow” the title settles into the top panel as the pixel presenter rises into the lower panel. The blue O floods the panel and contracts into the first node of a four-node workflow (Enquiries → Follow-ups → Documents → Updates); “AI AUTOMATION” types out and the nodes light in turn.",
 "problem": "Electric-blue panel. Inbox, Follow-ups, Team chat and Weekly report cards land one per spoken word from different directions; count badges pop on “Small jobs”; on “interrupting” the pile compresses into one tidy queue.",
 "a1": "“01 / CAPTURE ENQUIRIES” masked reveal; step tracker Enquiry → CRM → AI draft → Review. An enquiry arrives; name and email lift out and land in a CRM record; “Saved ✓” stamps on “CRM”. An AI draft writes itself; a Human review panel appears and a cursor clicks Approve on “review”.",
 "a2": "“02 / FOLLOW UP”. A Day 1 / Day 3 / Day 7 timeline draws; the lead card rides it; Day 3 fires a reminder on “reminders”; an approved message flies to the lead (“Sent ✓”); the lead moves to Day 7 and is flagged “Needs attention”.",
 "a3": "“03 / PROCESS DOCUMENTS”. An invoice arrives, a scan passes on “Extract”, four labelled fields separate out on “key details”, then page and fields collapse into an AI summary card; “Ready for the team to check” ticks on “check”.",
 "a4": "“04 / KEEP TEAMS UPDATED”. Task card flips In progress → Done on “changes”; a summary chip appears on “useful”; updates travel along wires to Sales, Operations and Finance, which confirm “Updated ✓” on “right people”.",
 "key": "Full-screen takeover. “THE KEY?” slams in, then becomes the label. The full workflow runs with ticks (CONNECTED TOOLS), rule chips land on the connectors (CLEAR RULES), then one step raises an exception that branches to a Human review card (HUMAN REVIEW). Emphasis words swap below the caption band.",
 "cta": "Full-screen call to action, held 12 s. “Want this workflow?”; a comment box types “WORKFLOW” and posts it; an inbox notification “Your workflow guide is here ✓” arrives on “inbox”; a big pill reads COMMENT “WORKFLOW” below; a cursor clicks + Follow → Following ✓ on “Follow for more”. All motion ends by about 7 s, then the frame holds to the last frame.",
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
