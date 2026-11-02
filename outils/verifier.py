#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verifier.py : le code de votre page dit-il vrai ?

Relit la page construite (par défaut _site/index.html), extrait le bloc
JSON-LD, vérifie qu'il est un JSON valide, qu'il décrit bien une Person,
puis que CHAQUE valeur qu'il affirme figure dans le texte visible de la
page (ou dans un lien visible, pour les adresses web). Il contrôle aussi
que moi.md reprend les mêmes faits mot pour mot et que llms.txt pointe
vers moi.md.

Utilisation :
  python3 outils/verifier.py              # vérifie _site/
  python3 outils/verifier.py exemple      # vérifie le dossier exemple/
  python3 outils/verifier.py chemin/vers/index.html

Code de sortie : 0 si tout est juste, 1 s'il y a un problème à corriger,
2 si la page est introuvable.

Python 3.8 ou plus récent, bibliothèque standard uniquement.
"""

import json
import os
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

RACINE = Path(__file__).resolve().parent.parent

# Propriétés qu'une page d'entité Person devrait toujours avoir.
ATTENDUES = [
    ("@id", "l'identifiant unique de l'entité (son numéro de dossier)"),
    ("name", "le nom"),
    ("jobTitle", "le métier"),
    ("description", "la phrase d'identité"),
    ("url", "l'adresse de la page"),
    ("worksFor", "l'employeur ou le projet"),
    ("address.addressLocality", "la ville"),
    ("knowsAbout", "les domaines de compétence"),
    ("sameAs", "les profils ailleurs (LinkedIn…)"),
]

CLES_TECHNIQUES = {"@context", "@type", "@id"}


# ---------------------------------------------------------------------------
# Lecture du HTML : texte visible, liens visibles, blocs JSON-LD
# ---------------------------------------------------------------------------

class _Lecteur(HTMLParser):
    """Sépare ce qu'un humain voit (texte, liens) de ce qu'il ne voit pas."""

    VIDES = {"area", "base", "br", "col", "embed", "hr", "img", "input",
             "link", "meta", "param", "source", "track", "wbr"}
    INVISIBLES = {"head", "script", "style", "template", "noscript", "title"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pile = []          # (balise, cachée ?)
        self.morceaux = []      # texte visible
        self.liens = []         # href des liens visibles
        self.jsonld = []        # contenu brut des blocs JSON-LD
        self._dans_jsonld = False
        self._tampon = []

    def _cache(self):
        return any(c for _, c in self.pile)

    def _ouvre(self, tag, attrs, pousser):
        a = {k.lower(): (v or "") for k, v in attrs}
        style = a.get("style", "").replace(" ", "").lower()
        cache = (tag in self.INVISIBLES or "hidden" in a
                 or "display:none" in style or "visibility:hidden" in style)
        if tag == "script" and a.get("type", "").strip().lower() == "application/ld+json":
            self._dans_jsonld = True
            self._tampon = []
        if tag == "a" and a.get("href") and not cache and not self._cache():
            self.liens.append(a["href"].strip())
        self.morceaux.append(" ")
        if pousser and tag not in self.VIDES:
            self.pile.append((tag, cache))

    def handle_starttag(self, tag, attrs):
        self._ouvre(tag, attrs, True)

    def handle_startendtag(self, tag, attrs):
        self._ouvre(tag, attrs, False)

    def handle_endtag(self, tag):
        if tag == "script" and self._dans_jsonld:
            self.jsonld.append("".join(self._tampon))
            self._dans_jsonld = False
        for i in range(len(self.pile) - 1, -1, -1):
            if self.pile[i][0] == tag:
                del self.pile[i:]
                break
        self.morceaux.append(" ")

    def handle_data(self, data):
        if self._dans_jsonld:
            self._tampon.append(data)
            return
        if not self._cache():
            self.morceaux.append(data)


def lire_html(html):
    """Renvoie (texte visible, liste des liens visibles, blocs JSON-LD bruts)."""
    lecteur = _Lecteur()
    lecteur.feed(html)
    lecteur.close()
    texte = re.sub(r"\s+", " ", "".join(lecteur.morceaux)).strip()
    return texte, lecteur.liens, lecteur.jsonld


# ---------------------------------------------------------------------------
# Comparaisons tolérantes (casse, espaces, apostrophes typographiques)
# ---------------------------------------------------------------------------

def normaliser(s):
    s = unicodedata.normalize("NFKC", str(s))
    s = (s.replace("\u2019", "'").replace("\u2018", "'")
          .replace("\u00a0", " ").replace("\u202f", " "))
    return re.sub(r"\s+", " ", s).strip().casefold()


def normaliser_url(u):
    u = str(u).strip()
    p = urlsplit(u)
    if not p.scheme:
        return u.rstrip("/").casefold()
    chemin = p.path.rstrip("/")
    reste = ("?" + p.query if p.query else "") + ("#" + p.fragment if p.fragment else "")
    return "%s://%s%s%s" % (p.scheme.lower(), p.netloc.lower(), chemin, reste)


def est_url(v):
    return isinstance(v, str) and re.match(r"^https?://", v.strip(), re.I) is not None


def sans_schema(u):
    return re.sub(r"^https?://(www\.)?", "", u.strip(), flags=re.I).rstrip("/")


# ---------------------------------------------------------------------------
# Parcours du JSON-LD
# ---------------------------------------------------------------------------

def noeuds(donnees):
    """Liste des objets de premier niveau (gère @graph et les tableaux)."""
    if isinstance(donnees, list):
        out = []
        for d in donnees:
            out.extend(noeuds(d))
        return out
    if isinstance(donnees, dict) and "@graph" in donnees:
        return [n for n in donnees["@graph"] if isinstance(n, dict)]
    if isinstance(donnees, dict):
        return [donnees]
    return []


def types_de(noeud):
    t = noeud.get("@type", [])
    return t if isinstance(t, list) else [t]


def valeurs(obj, chemin=""):
    """Toutes les valeurs affirmées, avec leur chemin (ex. worksFor.name)."""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in CLES_TECHNIQUES or k == "@graph":
                if k == "@graph":
                    for i, n in enumerate(v if isinstance(v, list) else [v]):
                        out.extend(valeurs(n, "@graph[%d]" % i))
                continue
            out.extend(valeurs(v, (chemin + "." + k) if chemin else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(valeurs(v, "%s[%d]" % (chemin, i)))
    elif isinstance(obj, bool):
        out.append((chemin, "true" if obj else "false"))
    elif isinstance(obj, (int, float)):
        out.append((chemin, str(obj)))
    elif isinstance(obj, str):
        out.append((chemin, obj))
    return out


def lire_chemin(noeud, chemin):
    cur = noeud
    for morceau in chemin.split("."):
        if isinstance(cur, dict) and morceau in cur:
            cur = cur[morceau]
        else:
            return None
    return cur


def ids_references(obj, out=None):
    """Toutes les références {"@id": ...} sans autre propriété."""
    if out is None:
        out = []
    if isinstance(obj, dict):
        if set(obj.keys()) == {"@id"}:
            out.append(obj["@id"])
        for k, v in obj.items():
            ids_references(v, out)
    elif isinstance(obj, list):
        for v in obj:
            ids_references(v, out)
    return out


def ids_definis(obj, out=None):
    if out is None:
        out = set()
    if isinstance(obj, dict):
        if "@id" in obj and len(obj) > 1:
            out.add(obj["@id"])
        for v in obj.values():
            ids_definis(v, out)
    elif isinstance(obj, list):
        for v in obj:
            ids_definis(v, out)
    return out


# ---------------------------------------------------------------------------
# La vérification elle-même
# ---------------------------------------------------------------------------

class Rapport:
    def __init__(self, titre):
        self.titre = titre
        self.lignes = []      # (niveau, texte) ; niveau : ok, probleme, conseil, info
        self.table = []       # (propriete, valeur, verdict)

    def ok(self, t):
        self.lignes.append(("ok", t))

    def probleme(self, t):
        self.lignes.append(("probleme", t))

    def conseil(self, t):
        self.lignes.append(("conseil", t))

    def info(self, t):
        self.lignes.append(("info", t))

    @property
    def nb_problemes(self):
        return sum(1 for n, _ in self.lignes if n == "probleme")

    def texte(self):
        marque = {"ok": "[OK]        ", "probleme": "[À CORRIGER]", "conseil": "[CONSEIL]   ",
                  "info": "            "}
        out = [self.titre, ""]
        for niveau, t in self.lignes:
            out.append("  %s %s" % (marque[niveau], t))
        if self.table:
            largeur = max(len(p) for p, _, _ in self.table)
            out += ["", "  Propriété par propriété (ce que dit le code, et si on le voit sur la page) :"]
            for p, v, verdict in self.table:
                v2 = v if len(v) <= 58 else v[:55] + "…"
                out.append("    %-*s  %-62s %s" % (largeur, p, "« %s »" % v2, verdict))
        out.append("")
        if self.nb_problemes == 0:
            out.append("Résultat : aucun problème. Le code dit vrai : tout ce qu'il affirme se voit sur la page.")
        else:
            out.append("Résultat : %d problème(s) à corriger. Corrigez fiche.json (pas index.html), "
                       "puis enregistrez : l'Action reconstruira la page." % self.nb_problemes)
        return "\n".join(out)

    def markdown(self):
        out = ["## Vérification : le code dit-il vrai ?", ""]
        for niveau, t in self.lignes:
            mark = {"ok": "OK", "probleme": "**À corriger**", "conseil": "Conseil", "info": ""}[niveau]
            out.append("- %s %s" % (mark, t) if mark else "- %s" % t)
        if self.table:
            out += ["", "| Propriété du JSON-LD | Valeur | Visible sur la page ? |", "|---|---|---|"]
            for p, v, verdict in self.table:
                v2 = v.replace("|", "\\|")
                if len(v2) > 70:
                    v2 = v2[:67] + "…"
                out.append("| `%s` | %s | %s |" % (p, v2, verdict))
        out.append("")
        out.append("**Aucun problème.**" if self.nb_problemes == 0
                   else "**%d problème(s) à corriger.**" % self.nb_problemes)
        return "\n".join(out) + "\n"


def verifier_html(html, rapport, nom_fichier="index.html"):
    """Vérifie le JSON-LD d'une page. Renvoie (personne, valeurs) pour la suite."""
    texte, liens, blocs = lire_html(html)
    texte_n = normaliser(texte)
    liens_n = {normaliser_url(h) for h in liens}

    if not blocs:
        rapport.probleme("Aucun bloc <script type=\"application/ld+json\"> dans %s : "
                         "les machines n'ont pas de fiche d'identité à lire." % nom_fichier)
        return None, []

    donnees = []
    for i, brut in enumerate(blocs, 1):
        try:
            donnees.append(json.loads(brut))
        except json.JSONDecodeError as e:
            rapport.probleme("Le bloc JSON-LD n° %d n'est pas un JSON valide (ligne %d, colonne %d du bloc : %s)."
                             % (i, e.lineno, e.colno, e.msg))
    if not donnees:
        return None, []
    rapport.ok("%d bloc(s) JSON-LD trouvé(s), JSON valide." % len(donnees))

    tous = []
    for d in donnees:
        ctx = d.get("@context") if isinstance(d, dict) else None
        if isinstance(d, dict) and not (isinstance(ctx, str) and "schema.org" in ctx):
            rapport.probleme("Le bloc JSON-LD n'a pas de \"@context\": \"https://schema.org\" : "
                             "sans lui, les machines ne savent pas quel vocabulaire vous parlez.")
        tous.extend(noeuds(d))

    personnes = [n for n in tous if "Person" in types_de(n)]
    if not personnes:
        rapport.probleme("Aucune entité de type Person dans le JSON-LD.")
        return None, []
    personne = personnes[0]
    rapport.ok("Entité principale : Person « %s »." % personne.get("name", "?"))

    # L'identifiant et l'adresse
    pid = personne.get("@id", "")
    purl = personne.get("url", "")
    if pid:
        if not est_url(pid):
            rapport.probleme("L'@id « %s » n'est pas une adresse web complète (https://…)." % pid)
        elif purl and not normaliser_url(pid).startswith(normaliser_url(purl)):
            rapport.probleme("L'@id « %s » ne commence pas par l'url « %s » : l'identifiant doit "
                             "appartenir à votre site." % (pid, purl))
        else:
            rapport.ok("@id : %s" % pid)
    # Les propriétés attendues
    manquantes = [(p, d) for p, d in ATTENDUES if lire_chemin(personne, p) in (None, "", [])]
    for p, d in manquantes:
        rapport.conseil("Propriété « %s » absente (%s)." % (p, d))
    wf = personne.get("worksFor")
    if isinstance(wf, dict) and not wf.get("@id"):
        rapport.conseil("worksFor n'a pas d'@id : donnez-lui le sien pour que l'organisation soit une entité à part entière.")

    # Les références @id doivent pointer vers quelque chose de défini
    definis = set()
    for d in donnees:
        definis |= ids_definis(d)
    for ref in ids_references(donnees):
        if ref not in definis:
            rapport.probleme("La référence {\"@id\": \"%s\"} ne pointe vers aucune entité décrite dans la page." % ref)

    # La règle d'or : chaque valeur affirmée est visible
    affirmees = []
    for d in donnees:
        affirmees.extend(valeurs(d))
    invisibles = 0
    for chemin, v in affirmees:
        if not str(v).strip():
            rapport.probleme("La propriété « %s » est vide : retirez-la ou remplissez-la." % chemin)
            continue
        if est_url(v):
            vu = (normaliser_url(v) in liens_n or normaliser(v) in texte_n
                  or normaliser(sans_schema(v)) in texte_n)
            verdict = "oui (lien visible)" if normaliser_url(v) in liens_n else ("oui" if vu else "NON")
        else:
            vu = normaliser(v) in texte_n
            verdict = "oui" if vu else "NON"
        rapport.table.append((chemin, str(v), verdict))
        if not vu:
            invisibles += 1
            rapport.probleme("« %s » (%s) est affirmé dans le JSON-LD mais ne se voit nulle part sur la page."
                             % (v, chemin))
    if invisibles == 0:
        rapport.ok("Les %d valeurs du JSON-LD se voient toutes sur la page (règle d'or respectée)."
                   % len(affirmees))
    return personne, affirmees


def verifier_dossier(dossier, rapport=None):
    """Vérifie index.html, moi.md et llms.txt d'un dossier construit."""
    dossier = Path(dossier)
    if dossier.is_file():
        page = dossier
        dossier = page.parent
    else:
        page = dossier / "index.html"
    if rapport is None:
        rapport = Rapport("Vérification de %s" % _joli(page))
    if not page.exists():
        rapport.probleme("Page introuvable : %s. Lancez d'abord outils/construire.py." % _joli(page))
        return rapport

    html = page.read_text(encoding="utf-8")
    personne, affirmees = verifier_html(html, rapport, page.name)

    # Le jumeau Markdown
    md = dossier / "moi.md"
    if not md.exists():
        rapport.probleme("moi.md est absent : les robots IA n'ont pas de version texte de la page.")
    elif affirmees:
        md_n = normaliser(md.read_text(encoding="utf-8"))
        absents = [v for _, v in affirmees if str(v).strip() and normaliser(v) not in md_n]
        if absents:
            for v in absents:
                rapport.probleme("moi.md ne contient pas « %s » : la page et son jumeau ne disent pas la même chose." % v)
        else:
            rapport.ok("moi.md reprend les %d faits du JSON-LD mot pour mot." % len(affirmees))

    # Le sommaire pour les robots IA
    llms = dossier / "llms.txt"
    if not llms.exists():
        rapport.probleme("llms.txt est absent.")
    else:
        t = llms.read_text(encoding="utf-8")
        premiere = t.lstrip("\ufeff").splitlines()[0] if t.strip() else ""
        if not premiere.startswith("# "):
            rapport.probleme("llms.txt doit commencer par un titre « # Votre nom » (format llmstxt.org).")
        elif personne and normaliser(premiere[2:]) != normaliser(personne.get("name", "")):
            rapport.probleme("Le titre de llms.txt (« %s ») n'est pas le nom de la page (« %s »)."
                             % (premiere[2:], personne.get("name", "")))
        if "moi.md" not in t:
            rapport.probleme("llms.txt ne pointe pas vers moi.md.")
        else:
            rapport.ok("llms.txt est au format llmstxt.org et pointe vers moi.md.")

    for nom in ("robots.txt", "sitemap.xml"):
        if not (dossier / nom).exists():
            rapport.conseil("%s est absent." % nom)
    return rapport


def _joli(p):
    try:
        return str(Path(p).resolve().relative_to(RACINE))
    except ValueError:
        return str(p)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cible = Path(argv[0]) if argv else RACINE / "_site"
    if not cible.is_absolute() and not cible.exists():
        cible = RACINE / cible
    if not cible.exists():
        print("Introuvable : %s\nLancez d'abord : python3 outils/construire.py" % cible)
        return 2
    rapport = verifier_dossier(cible)
    print(rapport.texte())

    resume = os.environ.get("GITHUB_STEP_SUMMARY")
    if resume:
        with open(resume, "a", encoding="utf-8") as f:
            f.write(rapport.markdown())
    if os.environ.get("GITHUB_ACTIONS") == "true":
        for niveau, t in rapport.lignes:
            if niveau == "probleme":
                print("::error title=La page ne dit pas vrai::%s" % t.replace("%", "%25").replace("\n", "%0A"))
    return 0 if rapport.nb_problemes == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
