#!/usr/bin/env python3
"""Build a Vish lead-magnet PDF guide from a JSON content file.

Usage:
    python3 make_guide.py guide.json out.pdf [--png-dir DIR]

The layout is fixed (A4, white, Inter, blue accents, footer with page numbers):
    page 1      cover: brand row, title, overview table, optional three rules
    pages 2..   two workflows per page, each Trigger -> Steps -> Tools -> Human approval
    last page   "Start this week" checklist + booking invitation
Use an even number of workflows (2 or 4) for balanced pages, or set "pages" in the JSON.
Needs Node with Playwright (preinstalled in Claude Code cloud) and, for the PNG check, pypdfium2.
See ../../references/guide-pdf.md for the JSON schema.
"""
import html, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(HERE))
AVATAR = os.path.join(SKILL, "assets", "character", "avatar.png")

DEFAULT_CTA = {
    "label": "Want it built for you?",
    "heading": "I build AI agents around your business.",
    "lede": "In a free call, we’ll find the one workflow that frees up the most time for you and your team.",
    "button": "Book a free discovery call",
    "url": "https://cal.com/vishworkflows/discovery",
    "url_note": "online, shown in your time zone",
    "chat": "Reply <b>BUILD</b> to my Instagram DM with your business, your tools and the task that eats your time.",
    "email": "support@sritrilinga.com",
    "handle": "@vish.workflows",
    "call": ["Where your time goes today, and which task to automate first.",
             "The tools you already use, and how they would connect.",
             "A clear next step, with no obligation."],
}

e = html.escape


def steps(items):
    return '<ol class="steps">' + "".join(f"<li><span>{e(s)}</span></li>" for s in items) + "</ol>"


def cover(g):
    ov = g["overview"]
    cols = ov.get("columns", ["Automation", "Starts when", "You approve"])
    rows = "".join(
        f'<tr><td class="n">{i + 1:02d}</td><td class="name">{e(r[0])}</td><td>{e(r[1])}</td><td>{e(r[2])}</td></tr>'
        for i, r in enumerate(ov["rows"]))
    out = f'''
  <div class="brand"><img src="avatar.png" alt=""><div><b>Vish | AI Automation</b><span>@vish.workflows</span></div></div>
  <div class="cover-title">
    <div class="label">{e(g.get("kicker", "A practical guide for growing businesses"))}</div>
    <h1>{e(g["title"])}</h1>
    <p class="lede">{e(g["subtitle"])}</p>
  </div>
  <div class="overview">
    <h2>{e(ov.get("heading", "At a glance"))}</h2>
    <p class="intro">{e(ov["intro"])}</p>
    <table class="at-a-glance"><thead><tr><th></th>{"".join(f"<th>{e(c)}</th>" for c in cols)}</tr></thead><tbody>{rows}</tbody></table>
  </div>'''
    r = g.get("rules")
    if r:
        items = "".join(f'<div><h3>{e(x["title"])}</h3><p>{e(x["text"])}</p></div>' for x in r["items"])
        out += f'''
  <div class="reliable">
    <div class="label">{e(r.get("label", "What makes it reliable"))}</div>
    <h2>{e(r.get("heading", "Three rules that keep it working"))}</h2>
    <div class="rules">{items}</div>
  </div>'''
    return out


def workflow(i, w):
    tools = "".join(f"<p><b>{e(k)}:</b> {e(v)}</p>" for k, v in w["tools"])
    return f'''
  <article class="auto">
    <div class="label">{e(w.get("label", f"Automation {i + 1:02d}"))}</div>
    <h2>{e(w["name"])}</h2>
    <p class="goal">{e(w["goal"])}</p>
    <dl class="rows">
      <dt>Trigger</dt><dd>{e(w["trigger"])}</dd>
      <dt>Steps</dt><dd>{steps(w["steps"])}</dd>
      <dt>Tools</dt><dd class="tools">{tools}</dd>
    </dl>
    <div class="approve"><b>Human approval:</b> {e(w["approval"])}</div>
  </article>'''


def start(g):
    s = g["start"]
    items = "".join(f'<li><span><b>{e(x["lead"])}</b> {e(x["text"])}</span></li>' for x in s["items"])
    return f'''
  <div class="start">
    <div class="label">{e(s.get("label", "Your first steps"))}</div>
    <h2>{e(s.get("heading", "Start this week"))}</h2>
    <p class="intro">{e(s["intro"])}</p>
    <ul class="check">{items}</ul>
  </div>'''


def cta(g, alone):
    c = {**DEFAULT_CTA, **g.get("cta", {})}
    call = f'<div class="call"><h3>What we’ll cover</h3>{steps(c["call"])}</div>' if alone else ""
    short = c["url"].replace("https://", "")
    return f'''
  <div class="close{" alone" if alone else ""}">
    <div class="label">{e(c["label"])}</div>
    <h2>{e(c["heading"])}</h2>
    <p class="lede">{e(c["lede"])}</p>
    <a class="book" href="{e(c["url"])}">{e(c["button"])}</a>
    <p class="book-url"><a href="{e(c["url"])}">{e(short)}</a> · {e(c["url_note"])}</p>
    {call}
    <div class="contact">
      <div><h3>Prefer to chat?</h3><p class="muted">{c["chat"]}</p></div>
      <div><h3>Support</h3><p class="muted"><a href="mailto:{e(c["email"])}">{e(c["email"])}</a><br>Instagram: {e(c["handle"])}</p></div>
    </div>
  </div>'''


def auto_pages(n):
    pages = [["cover"]]
    for i in range(0, n - 1, 2):
        pages.append([f"wf:{i}", f"wf:{i + 1}"])
    if n % 2:
        print("note: odd number of workflows; the last page holds one workflow + start, then the CTA gets its own page."
              " Check the PNGs, or set \"pages\" in the JSON.", file=sys.stderr)
        pages += [[f"wf:{n - 1}", "start"], ["cta-alone"]]
    else:
        pages.append(["start", "cta"])
    return pages


def build_html(g):
    css = open(os.path.join(HERE, "guide.css"), encoding="utf-8").read()
    pages = g.get("pages") or auto_pages(len(g["workflows"]))
    body = []
    for p in pages:
        parts = []
        for b in p:
            if b == "cover": parts.append(cover(g))
            elif b.startswith("wf:"):
                i = int(b[3:]); parts.append(workflow(i, g["workflows"][i]))
            elif b == "start": parts.append(start(g))
            elif b == "cta": parts.append(cta(g, False))
            elif b == "cta-alone": parts.append(cta(g, True))
            else: raise SystemExit(f"unknown block {b!r}")
        body.append('<section class="page">' + "".join(parts) + "\n</section>")
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{e(g["title"])}</title>'
            f"<style>{css}</style></head><body>\n" + "\n".join(body) + "\n</body></html>")


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    src, out = sys.argv[1], os.path.abspath(sys.argv[2])
    png_dir = sys.argv[sys.argv.index("--png-dir") + 1] if "--png-dir" in sys.argv else None
    g = json.load(open(src, encoding="utf-8"))
    work = tempfile.mkdtemp(prefix="vish-guide-")
    shutil.copytree(os.path.join(HERE, "fonts"), os.path.join(work, "fonts"))
    shutil.copy(AVATAR, os.path.join(work, "avatar.png"))
    page = os.path.join(work, "guide.html")
    open(page, "w", encoding="utf-8").write(build_html(g))
    footer = g.get("footer", f'{g["title"]} · Vish | AI Automation · @vish.workflows')
    subprocess.run(["node", os.path.join(HERE, "render.js"), page, out, footer], check=True)
    shutil.copy(page, os.path.splitext(out)[0] + ".html")  # keep the generated source next to the PDF

    # Self-check: page count, links, and PNGs of every page to inspect by eye.
    try:
        import pypdf
        r = pypdf.PdfReader(out)
        links = [a.get_object()["/A"]["/URI"] for pg in r.pages for a in (pg.get("/Annots") or [])
                 if "/A" in a.get_object()]
        print(f"pages: {len(r.pages)}  links: {links}")
    except ImportError:
        print("pypdf not installed; skipped link check")
    if png_dir:
        import pypdfium2 as pdfium
        os.makedirs(png_dir, exist_ok=True)
        for i, pg in enumerate(pdfium.PdfDocument(out)):
            pg.render(scale=1.6).to_pil().save(os.path.join(png_dir, f"page-{i + 1}.png"))
        print(f"page PNGs in {png_dir}: inspect every one before delivering")


if __name__ == "__main__":
    main()
