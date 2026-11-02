#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
documents.py : pour le formateur, pas pour les étudiantes.

Régénère les documents dérivés après une modification de docs/guide-installation.md
ou d'un fichier de gems/ :
  - docs/gems.md (assemblé depuis gems/*.md)
  - README.md (en-tête + docs/guide-installation.md + inventaire)
  - docs/guide-installation.pdf et docs/gems.pdf (Chromium, via Playwright)

Prérequis : pip install markdown playwright && playwright install chromium
Utilisation : python3 outils/documents.py
"""
import re, sys, html
from pathlib import Path
import markdown
from playwright.sync_api import sync_playwright

DEPOT = Path(__file__).resolve().parent.parent
POL = DEPOT / "themes" / "polices"

CSS = """
@font-face { font-family: "Instrument Sans"; src: url("file://%(pol)s/instrument-sans.woff2") format("woff2"); font-weight: 400 700; font-stretch: 75%% 100%%; }
@font-face { font-family: "Newsreader"; src: url("file://%(pol)s/newsreader.woff2") format("woff2"); font-weight: 200 800; }
@font-face { font-family: "Newsreader"; src: url("file://%(pol)s/newsreader-italique.woff2") format("woff2"); font-weight: 200 800; font-style: italic; }
@page { size: A4; margin: 18mm 17mm 20mm 17mm; }
:root { --encre:#141A26; --encre2:#3E4757; --encre3:#5B6475; --ligne:#DDE1E8; --accent:#2952CC; --fond-encadre:#EEF2FB; --fond-code:#F3F4F7; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; color: var(--encre); font-family: "Instrument Sans", sans-serif; font-size: 10.4pt; line-height: 1.5; }
.couverture { padding: 26mm 0 10mm; border-bottom: 1px solid var(--ligne); margin-bottom: 8mm; }
.couverture .sur-titre { color: var(--encre3); font-size: 10pt; margin: 0 0 5mm; }
.couverture h1 { font-stretch: 78%%; font-weight: 700; font-size: 34pt; line-height: 1; letter-spacing: -.02em; margin: 0; }
.couverture .trait { display: block; width: 22mm; height: 2.2mm; background: var(--accent); margin: 7mm 0 6mm; }
.couverture .chapo { font-size: 12.5pt; line-height: 1.45; color: var(--encre2); max-width: 150mm; margin: 0; }
h1 { font-stretch: 78%%; font-weight: 700; font-size: 24pt; line-height: 1.05; margin: 0 0 4mm; }
h2 { font-stretch: 85%%; font-weight: 700; font-size: 15.5pt; line-height: 1.2; margin: 9mm 0 3mm; padding-top: 3mm; border-top: 2px solid var(--encre); break-after: avoid; }
h2.etape { display: flex; gap: 3.5mm; align-items: baseline; }
h2.etape .num { display: inline-grid; place-items: center; min-width: 9mm; height: 9mm; border-radius: 2mm; background: var(--accent); color: #fff; font-size: 13pt; font-stretch: 100%%; flex: none; transform: translateY(1.2mm); }
h2.saut { break-before: page; }
h3 { font-size: 11.5pt; margin: 6mm 0 2mm; break-after: avoid; }
p { margin: 0 0 2.6mm; }
ol, ul { margin: 0 0 3mm; padding-left: 6mm; }
li { margin: 1.1mm 0; }
li > ul { margin-top: 1mm; }
strong { font-weight: 650; }
a { color: var(--accent); text-decoration: none; }
code { font-family: "JetBrains Mono", "DejaVu Sans Mono", monospace; font-size: 8.6pt; background: var(--fond-code); padding: .2mm 1mm; border-radius: 1mm; }
pre { background: var(--fond-code); border: 1px solid var(--ligne); border-radius: 2mm; padding: 3mm 3.5mm; margin: 0 0 3mm; white-space: pre-wrap; word-wrap: break-word; font-size: 8.3pt; line-height: 1.45; }
pre code { background: none; padding: 0; font-size: inherit; }
blockquote { margin: 3mm 0 4mm; padding: 3mm 4mm; background: var(--fond-encadre); border-left: 1.4mm solid var(--accent); border-radius: 0 2mm 2mm 0; break-inside: avoid; }
blockquote p { margin: 0 0 1.5mm; }
blockquote p:last-child { margin: 0; }
table { width: 100%%; border-collapse: collapse; margin: 1mm 0 4mm; font-size: 9.4pt; break-inside: avoid; }
th { text-align: left; font-weight: 650; border-bottom: 1.5px solid var(--encre); padding: 1.6mm 2mm; }
td { border-bottom: 1px solid var(--ligne); padding: 1.6mm 2mm; vertical-align: top; }
tr { break-inside: avoid; }
hr { display: none; }
.ok { margin: 2mm 0 3mm; padding: 2.2mm 3.5mm; border: 1px solid #B9D7C7; background: #EEF7F1; border-radius: 2mm; break-inside: avoid; }
.ok strong:first-child { color: #1F6B4F; }
.pied { margin-top: 8mm; color: var(--encre3); font-size: 8.6pt; border-top: 1px solid var(--ligne); padding-top: 3mm; }
"""

def assembler():
    D = DEPOT
    # docs/gems.md : on garde l'intro existante, on régénère les 4 Gems
    g = (D / "docs/gems.md").read_text(encoding="utf-8")
    intro = g.split("---\n\n## Gem 1", 1)[0]
    parts = [intro.rstrip() + "\n"]
    for f in sorted((D / "gems").glob("*.md")):
        t = f.read_text(encoding="utf-8")
        t = re.sub(r"\nPour le créer : Gemini > .*?\n", "\n", t)
        t = re.sub(r"^# ", "## ", t, count=1, flags=re.M)
        t = re.sub(r"^## (Nom|Description|Instructions|Tester tout de suite)$", r"### \1", t, flags=re.M)
        parts.append("---\n\n" + t.strip() + "\n")
    parts.append("---\n\nSource : dossier `gems/` du dépôt. Ce document est assemblé à partir de ces quatre fichiers ; en cas d'écart, ce sont eux qui font foi.\n")
    (D / "docs/gems.md").write_text("\n".join(parts), encoding="utf-8")
    # README : en-tête + guide + inventaire
    r = (D / "README.md").read_text(encoding="utf-8")
    entete = r.split("## Le parcours en un coup d'œil", 1)[0]
    inventaire = "---\n\n## Ce que contient la mallette" + r.split("## Ce que contient la mallette", 1)[1]
    guide = (D / "docs/guide-installation.md").read_text(encoding="utf-8")
    corps = "## Le parcours en un coup d'œil" + guide.split("## Le parcours en un coup d'œil", 1)[1]
    # l'en-tête du README reprend le chapô et l'encadré du guide
    chapo = guide.split("\n", 1)[1].split("## Le parcours en un coup d'œil", 1)[0].strip()
    entete_base = entete.split("**Ce que vous allez obtenir**", 1)[0]
    (D / "README.md").write_text(entete_base + chapo + "\n\n" + corps.rstrip() + "\n\n" + inventaire, encoding="utf-8")
    print("gems.md et README régénérés")

def construire(md_path, out_pdf, sur_titre, saut_avant=()):
    md = Path(md_path).read_text(encoding="utf-8")
    titre = re.match(r"# (.+)", md).group(1)
    md = md.split("\n", 1)[1]
    # chapô : le premier paragraphe après le titre
    md = md.lstrip()
    chapo, reste = md.split("\n\n", 1)
    # python-markdown veut 4 espaces pour une sous-liste (GitHub en accepte 3)
    reste = re.sub(r"(?m)^   ([-*] )", r"    \1", reste)
    corps = markdown.markdown(reste, extensions=["tables", "fenced_code", "sane_lists"])
    # Les « C'est bon quand » deviennent des encadrés verts
    corps = re.sub(r"<p><strong>C'est bon quand</strong>(.*?)</p>", r'<p class="ok"><strong>C&#x27;est bon quand</strong>\1</p>', corps)
    corps = re.sub(r"<p><strong>C&#x27;est bon quand</strong>(.*?)</p>", r'<p class="ok"><strong>C&#x27;est bon quand</strong>\1</p>', corps)
    # Les titres d'étape numérotés
    def etape(m):
        n, t = m.group(1), m.group(2)
        return '<h2 class="etape"><span class="num">%s</span><span>%s</span></h2>' % (n, t)
    corps = re.sub(r"<h2>Étape (\d+) · (.*?)</h2>", etape, corps)
    for t in saut_avant:
        corps = corps.replace("<h2>%s" % t, '<h2 class="saut">%s' % t, 1)
    # espaces insécables à l'intérieur des guillemets français (pas de « orphelin en fin de ligne)
    # ... mais jamais dans le code ni dans les blocs à copier.
    def typo(t):
        t = t.replace("« ", "«\u00a0").replace(" »", "\u00a0»")
        return re.sub(r" ([:;?!])", "\u00a0\\1", t)
    morceaux = re.split(r"(<pre>.*?</pre>|<code>.*?</code>|<[^>]+>)", corps, flags=re.S)
    corps = "".join(m if m.startswith("<") else typo(m) for m in morceaux)
    chapo_html = markdown.markdown(chapo)
    chapo_html = chapo_html.replace("<p>", '<p class="chapo">', 1)
    morceaux = re.split(r"(<code>.*?</code>|<[^>]+>)", chapo_html, flags=re.S)
    chapo_html = "".join(m if m.startswith("<") else typo(m) for m in morceaux)
    page = """<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>%s</title><style>%s</style></head><body>
<header class="couverture"><p class="sur-titre">%s</p><h1>%s</h1><span class="trait"></span>%s</header>
%s
<p class="pied">Mallette du TP « Votre page d'entité » · github.com/agencekoeki/mba-mdia-page-entite · version du 2 novembre 2026.</p>
</body></html>""" % (html.escape(titre), CSS % {"pol": POL}, html.escape(sur_titre), html.escape(titre), chapo_html, corps)
    tmp = Path(TMP) / (Path(out_pdf).stem + ".html")
    tmp.write_text(page, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto("file://%s" % tmp)
        pg.wait_for_timeout(500)
        pg.pdf(path=str(out_pdf), format="A4", print_background=True, display_header_footer=True,
               header_template="<span></span>",
               footer_template='<div style="width:100%%;font-family:sans-serif;font-size:7.5pt;color:#5B6475;padding:0 17mm;display:flex;justify-content:space-between"><span>%s</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>' % html.escape(titre),
               margin={"top": "16mm", "bottom": "18mm", "left": "17mm", "right": "17mm"})
        b.close()
    print("PDF :", out_pdf)

import tempfile
TMP = tempfile.mkdtemp(prefix="documents-")
assembler()
construire(DEPOT / "docs/guide-installation.md", DEPOT / "docs/guide-installation.pdf",
           "MBA Marketing Digital et IA · De Vinci · Module SEO & GEO · TP du 3 novembre 2026",
           saut_avant=("Si ça bloque", "Ce que vous apprenez"))
construire(DEPOT / "docs/gems.md", DEPOT / "docs/gems.pdf",
           "MBA Marketing Digital et IA · De Vinci · Module SEO & GEO · TP du 3 novembre 2026",
           saut_avant=("Gem 2", "Gem 3", "Gem 4"))
