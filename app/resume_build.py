"""Build resume.txt (for the AI agent) and resume.pdf (public CV download) from resume.yaml.
The phone number is deliberately left out of both outputs."""
import pathlib
from xml.sax.saxutils import escape as esc


def parse(text):
    """Parse and check resume YAML text. Raises ValueError with a message a human can act on."""
    import yaml
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        mark = getattr(e, "problem_mark", None)
        where = f" (line {mark.line + 1}, column {mark.column + 1})" if mark else ""
        raise ValueError(f"This is not valid YAML{where}: {getattr(e, 'problem', None) or e}") from e
    if not isinstance(data, dict) or not isinstance(data.get("resume"), dict):
        raise ValueError("The file must start with a top-level 'resume:' section.")
    r = data["resume"]
    try:
        build_text(r)
    except KeyError as e:
        raise ValueError(f"Missing field: {e}. Compare with tools/resume.yaml for the expected layout.") from e
    except (TypeError, AttributeError) as e:
        raise ValueError(f"A section has the wrong shape ({e}). Compare with tools/resume.yaml.") from e
    return r


def load(src):
    return parse(pathlib.Path(src).read_text(encoding="utf-8"))


def build_text(r):
    c = r["contact"]
    L = [r["name"], r["title"], r["summary"], f"Email: {c['email']} | LinkedIn: {c['linkedin']} | GitHub: {c['github']} | {c['address']}", "", "COMPETENCES"]
    for g in r["technical_expertise"]:
        L.append(f"{g['resume_title']}: {', '.join(g['skills'])}")
    L += ["", "LANGUES"] + [f"{x['language']}: {x['proficiency']}" for x in r["languages"]]
    L += ["", "EXPERIENCE"]
    for e in r["professional_experience"]:
        L.append(f"{e['position']} - {e['company']} ({e['location']}, {e['duration']})")
        L += ["- " + a for a in e["achievements"]]
    L += ["", "PROJETS"]
    for p in r["independent_projects"]:
        L.append(f"{p['name']} ({p['location']}, {p['duration']}): {p['description']}")
        L += ["- " + a for a in p["achievements"]] + ["Impact: " + p["impact"]]
    L += ["", "FORMATION"]
    for e in r["education"]:
        L.append(f"{e['program']} - {e['institution']} ({e['location']}, {e['duration']})" + (f". {e['details']}" if e.get("details") else ""))
    return "\n".join(L) + "\n"


def build_pdf(r, out):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

    c = r["contact"]
    ember = colors.HexColor("#C25A00")
    S = lambda n, **k: ParagraphStyle(n, fontName=k.pop("f", "Helvetica"), **k)
    name, sub = S("n", fontSize=22, leading=26, f="Helvetica-Bold"), S("s", fontSize=10.5, leading=14, textColor=ember)
    h, b = S("h", fontSize=10, leading=13, f="Helvetica-Bold", textColor=ember, spaceBefore=9, spaceAfter=3), S("b", fontSize=9, leading=12)
    it, bl = S("i", fontSize=9.3, leading=12, f="Helvetica-Bold", spaceBefore=4), S("l", fontSize=9, leading=12, leftIndent=10, bulletIndent=0)
    st = [Paragraph(esc(r["name"]), name), Paragraph(esc(r["title"]), sub), Spacer(1, 3),
          Paragraph(esc(f"{c['email']}  ·  {c['linkedin'].replace('https://', '')}  ·  {c['github'].replace('https://', '')}  ·  {c['address']}"), b),
          Spacer(1, 3), Paragraph(esc(r["summary"]), b)]
    def sec(t): st.append(Paragraph(t, h))
    def item(t, bullets=()):
        st.append(Paragraph(esc(t), it)); [st.append(Paragraph(esc(x), bl, bulletText="•")) for x in bullets]
    sec("COMPÉTENCES")
    for g in r["technical_expertise"]: st.append(Paragraph(f"<b>{esc(g['resume_title'])}</b> : {esc(', '.join(g['skills']))}", b))
    sec("EXPÉRIENCE")
    for e in r["professional_experience"]: item(f"{e['position']} · {e['company']} · {e['duration']}", e["achievements"])
    sec("PROJETS")
    for p in r["independent_projects"]: item(f"{p['name']} · {p['duration']}", p["achievements"])
    sec("FORMATION")
    for e in r["education"]: item(f"{e['program']} · {e['institution']} · {e['duration']}", [e["details"]] if e.get("details") else [])
    sec("LANGUES"); st.append(Paragraph(esc(" · ".join(f"{x['language']} ({x['proficiency']})" for x in r["languages"])), b))
    tmp = pathlib.Path(out).with_suffix(".pdf.tmp")
    SimpleDocTemplate(str(tmp), pagesize=A4, leftMargin=16*mm, rightMargin=16*mm, topMargin=14*mm, bottomMargin=12*mm, title=r["name"] + " - CV").build(st)
    tmp.replace(out)


def build(src, out_dir):
    """Write resume.txt and resume.pdf into out_dir. Raises if the YAML is invalid, leaving old files untouched."""
    r = load(src)
    text = build_text(r)
    out_dir = pathlib.Path(out_dir)
    build_pdf(r, out_dir / "resume.pdf")
    tmp = out_dir / "resume.txt.tmp"
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(out_dir / "resume.txt")
