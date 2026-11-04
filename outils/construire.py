#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
construire.py : une fiche, tout le reste en découle.

Lit fiche.json (la fiche d'identité de votre entité), la vérifie, puis
fabrique dans _site/ :

  index.html    la page pour les humains, avec son bloc JSON-LD schema.org
  moi.md        le jumeau Markdown : les mêmes faits, mot pour mot
  llms.txt      le sommaire pour les robots IA (format llmstxt.org)
  robots.txt    qui peut lire le site (tout le monde)
  sitemap.xml   la liste des pages, pour les moteurs
  .nojekyll     « publie les fichiers tels quels »
  polices/      les polices du thème choisi

Version 2.1 (jour 2), trois champs optionnels de plus dans fiche.json :
  "photo"                votre photo (fichier envoyé dans le dépôt), affichée et déclarée (image)
  "verification_google"  le code de Search Console (méthode « Balise HTML »)
  "pages"                vos pages de contenu, écrites en Markdown dans pages/ :
                         chacune devient <nom>.html (avec un JSON-LD Article signé
                         par vous) et <nom>.md, reliée à la page d'accueil

Règle d'or, garantie par construction : la page visible, le JSON-LD et
moi.md sont tous écrits à partir des MÊMES faits (la fonction faits()).
Rien n'est inventé, rien n'est caché.

Utilisation :
  python3 outils/construire.py
  python3 outils/construire.py --fiche fiche.exemple.json --sortie exemple
  python3 outils/construire.py --url-base https://mon-identifiant.github.io/

Dans GitHub Actions, l'adresse de la page est déduite du nom du dépôt.

Code de sortie : 0 si la page est construite, 1 si la fiche est à
corriger (rien n'est construit), 2 si un fichier manque.

Python 3.8 ou plus récent, bibliothèque standard uniquement.
"""

import argparse
import difflib
import html
import json
import os
import re
import shutil
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

RACINE = Path(__file__).resolve().parent.parent
VERSION = "2.1"
THEMES = ("clair", "sombre", "editorial")
COULEUR_PAR_DEFAUT = "#2952CC"

# Les champs de fiche.json, dans l'ordre où on les explique (voir fiche.md).
CHAMPS = [
    "type", "nom", "phrase_identite", "metier", "employeur", "ville", "domaines",
    "ce_que_je_fais", "parcours", "profils", "entite_liee",
    "theme", "couleur_accent", "animations", "identifiant_github", "fictif",
    "photo", "verification_google", "pages",
]
OBLIGATOIRES = ["nom", "phrase_identite", "metier", "ville", "domaines", "identifiant_github"]

EXEMPLES = {
    "nom": '"nom": "Marie Exemple",',
    "phrase_identite": '"phrase_identite": "Marie Exemple est chargée de marketing digital chez Lumen, à Lyon.",',
    "metier": '"metier": "Chargée de marketing digital",',
    "ville": '"ville": "Lyon",',
    "domaines": '"domaines": ["Marketing digital", "SEO", "Emailing"],',
    "identifiant_github": '"identifiant_github": "marie-exemple",',
    "ce_que_je_fais": '"ce_que_je_fais": "Je prépare les campagnes d\'emailing de Lumen.",',
    "parcours": '"parcours": "Après une licence de communication, je suis le MBA MDIA en alternance.",',
    "theme": '"theme": "clair",',
    "couleur_accent": '"couleur_accent": "#2952CC",',
    "animations": '"animations": true,',
    "photo": '"photo": "photo.jpg",',
    "verification_google": '"verification_google": "le code donné par Search Console",',
    "pages": '"pages": ["pages/ma-premiere-page.md"],',
}

PLACEHOLDERS = ("prénom nom", "[", "…", "identifiant", "votre-profil", "votre métier", "xxx")

PLATEFORMES = {
    "linkedin.com": "LinkedIn", "github.com": "GitHub", "malt.fr": "Malt", "malt.com": "Malt",
    "x.com": "X", "twitter.com": "X", "instagram.com": "Instagram", "medium.com": "Medium",
    "youtube.com": "YouTube", "behance.net": "Behance", "dribbble.com": "Dribbble",
    "wikidata.org": "Wikidata", "welcometothejungle.com": "Welcome to the Jungle",
    "substack.com": "Substack", "tiktok.com": "TikTok", "facebook.com": "Facebook",
    "bsky.app": "Bluesky", "orcid.org": "ORCID", "scholar.google.com": "Google Scholar",
}

# Le mot que l'étudiante écrit pour sa place dans l'entité liée → la propriété schema.org.
RELATIONS = [
    # (début du mot, sans accents)    propriété      type attendu    sens
    (("cofond", "co-fond", "fond"), "founder", "Organization", "l'organisation a pour fondatrice cette personne"),
    (("membre", "benevole", "adherent", "president", "tresori", "secretaire", "vice-pres", "animat",
      "coordinat", "responsable", "salari"), "memberOf", "Organization", "la personne est membre de l'organisation"),
    (("autric", "auteur", "auteure", "coautric", "co-autric", "coauteur", "co-auteur", "redactri", "redacteur"),
     "author", "CreativeWork", "l'œuvre a pour autrice cette personne"),
    (("creatri", "createur", "cocreatri", "co-creatri", "realisatri", "realisateur", "conceptri", "concepteur"),
     "creator", "CreativeWork", "l'œuvre a pour créatrice cette personne"),
    (("contribut",), "contributor", "CreativeWork", "la personne a contribué à l'œuvre"),
]


# ---------------------------------------------------------------------------
# Petits outils
# ---------------------------------------------------------------------------

def sans_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def e(s):
    """Échappe un texte pour le HTML."""
    return html.escape(str(s), quote=True)


def joli_chemin(chemin):
    """profils[1].url → « profils », 2e élément, « url »"""
    morceaux = []
    for m in re.finditer(r"([^.\[\]]+)|\[(\d+)\]", chemin):
        if m.group(1):
            morceaux.append("« %s »" % m.group(1))
        else:
            n = int(m.group(2)) + 1
            morceaux.append("%s élément" % ("1er" if n == 1 else "%de" % n))
    return ", ".join(morceaux)


def couper_paragraphes(texte):
    return [p.strip() for p in re.split(r"\n\s*\n|\n", texte) if p.strip()]


# ---------------------------------------------------------------------------
# Couleurs et contraste (WCAG 2.x)
# ---------------------------------------------------------------------------

def hex_vers_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_vers_hex(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(c))) for c in rgb)


def luminance(h):
    def canal(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = hex_vers_rgb(h)
    return 0.2126 * canal(r) + 0.7152 * canal(g) + 0.0722 * canal(b)


def contraste(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def ajuster(couleur, fond, cible):
    """Assombrit (fond clair) ou éclaircit (fond sombre) jusqu'au contraste visé."""
    if contraste(couleur, fond) >= cible:
        return couleur
    vers = (0, 0, 0) if luminance(fond) > 0.4 else (255, 255, 255)
    r0 = hex_vers_rgb(couleur)
    for i in range(1, 101):
        t = i / 100
        c = rgb_vers_hex([r0[k] + (vers[k] - r0[k]) * t for k in range(3)])
        if contraste(c, fond) >= cible:
            return c
    return rgb_vers_hex(vers)


# ---------------------------------------------------------------------------
# Lecture et vérification de la fiche
# ---------------------------------------------------------------------------

class FicheInvalide(Exception):
    pass


class Journal:
    """Rassemble les erreurs (bloquantes) et les conseils (non bloquants)."""

    def __init__(self, texte_brut, nom_fichier):
        self.texte = texte_brut
        self.fichier = nom_fichier
        self.erreurs = []    # (chemin, probleme, a_faire, ligne)
        self.conseils = []   # (chemin, texte)

    def ligne_de(self, chemin):
        """Numéro de ligne d'un champ (ex. profils[1].url), en suivant le chemin."""
        if not chemin:
            return None
        jetons = re.findall(r"([^.\[\]]+)|\[(\d+)\]", chemin)
        pos, rang, trouve = 0, 0, None
        for cle, indice in jetons:
            if indice:
                rang = int(indice)
                continue
            motif = re.compile(r'"%s"\s*:' % re.escape(cle))
            m = None
            for _ in range(rang + 1):
                m = motif.search(self.texte, pos)
                if not m:
                    break
                pos = m.end()
            rang = 0
            if not m:
                break
            trouve = m
        if trouve is None:
            return None
        return self.texte.count("\n", 0, trouve.start()) + 1

    def erreur(self, chemin, probleme, a_faire):
        self.erreurs.append((chemin, probleme, a_faire, self.ligne_de(chemin)))

    def conseil(self, chemin, texte):
        self.conseils.append((chemin, texte))


def expliquer_json(err, texte):
    """Traduit une erreur de syntaxe JSON en français, avec la ligne fautive."""
    lignes = texte.splitlines() or [""]
    n = max(1, min(err.lineno, len(lignes)))
    ligne = lignes[n - 1]
    col = err.colno
    reste = texte[err.pos:].lstrip()
    car = texte[err.pos] if err.pos < len(texte) else ""
    avant = ligne[:max(0, col - 1)]
    precedente = n - 1
    while precedente > 0 and not lignes[precedente - 1].strip():
        precedente -= 1
    msg = err.msg

    if msg.startswith("Expecting ',' delimiter"):
        if not avant.strip() and precedente > 0:
            probleme = "il manque une virgule à la fin de la ligne %d." % precedente
            a_faire = ("ajoutez une virgule à la fin de la ligne %d. Chaque ligne \"champ\": valeur "
                       "se termine par une virgule, sauf la dernière avant } ou ]." % precedente)
        else:
            probleme = "il manque une virgule (ou un guillemet fermant) juste avant cet endroit."
            a_faire = ("vérifiez que le texte précédent se termine bien par un guillemet \", "
                       "puis séparez les éléments par une virgule.")
    elif msg.startswith("Illegal trailing comma") or (
            msg.startswith("Expecting property name") and reste[:1] == "}") or (
            msg.startswith("Expecting value") and car in "]}" and car):
        if msg.startswith("Illegal trailing comma"):
            ligne_virgule = n  # l'erreur pointe sur la virgule elle-même
        else:
            ligne_virgule = precedente if not avant.strip() else n
        probleme = "il y a une virgule en trop à la fin de la ligne %d, juste avant une fermeture } ou ]." % max(1, ligne_virgule)
        a_faire = ("supprimez cette virgule : le dernier élément d'une liste ou d'un objet "
                   "n'est jamais suivi d'une virgule.")
    elif car in "“”«»‘’":
        probleme = "des guillemets typographiques (%s) au lieu des guillemets droits." % car
        a_faire = ("remplacez “ ” « » par des guillemets droits \" (touche 3 du clavier français). "
                   "Astuce : demandez au Gem « Ma fiche d'entité » de renvoyer la fiche dans un bloc de code.")
    elif msg.startswith("Expecting property name"):
        probleme = "un nom de champ n'est pas entre guillemets droits."
        a_faire = 'écrivez le nom du champ entre guillemets droits, par exemple "ville": "Lyon"'
    elif msg.startswith("Expecting value"):
        mot = re.match(r"[A-Za-zÀ-ÿ_]+", reste)
        if not reste:
            probleme = "le fichier est vide ou s'arrête trop tôt."
            a_faire = "recollez la fiche complète, de la première accolade { à la dernière }."
        elif mot and mot.group(0).lower() in ("oui", "non", "vrai", "faux", "true", "false", "yes", "no"):
            probleme = "« %s » n'est pas une valeur JSON." % mot.group(0)
            a_faire = "pour oui ou non, écrivez true ou false, en minuscules et sans guillemets."
        else:
            probleme = "une valeur manque, ou un texte n'est pas entre guillemets."
            a_faire = 'mettez le texte entre guillemets droits, par exemple "ville": "Lyon"'
    elif msg.startswith("Unterminated string"):
        probleme = "un texte commence par un guillemet mais ne se termine jamais."
        a_faire = "ajoutez le guillemet fermant \" à la fin du texte, sur la même ligne."
    elif msg.startswith("Invalid control character"):
        probleme = "un texte est coupé par un retour à la ligne."
        a_faire = "remettez tout le texte sur une seule ligne, entre ses deux guillemets."
    elif msg.startswith("Expecting ':' delimiter"):
        probleme = "il manque les deux-points entre le nom du champ et sa valeur."
        a_faire = 'écrivez "champ": valeur, par exemple "ville": "Lyon"'
    elif msg.startswith("Extra data"):
        probleme = "il reste du texte après la dernière accolade }."
        a_faire = ("supprimez ce qui suit la dernière } (souvent un reste de copier-coller, "
                   "ou une accolade en trop).")
    elif msg.startswith("Invalid \\escape") or "escape" in msg:
        probleme = "une barre oblique inverse \\ est mal placée."
        a_faire = "supprimez-la, ou doublez-la (\\\\)."
    else:
        probleme = "erreur de syntaxe (%s)." % msg
        a_faire = "comparez votre fichier avec fiche.exemple.json, ou redemandez la fiche au Gem."

    pointeur = " " * (len(ligne[:max(0, col - 1)].expandtabs(4))) + "^"
    return n, col, ligne.expandtabs(4), pointeur, probleme, a_faire


def lire_fiche(chemin):
    """Renvoie (texte brut nettoyé, objet JSON). Lève FicheInvalide avec un message français."""
    if not chemin.exists():
        raise FileNotFoundError(chemin)
    brut = chemin.read_text(encoding="utf-8-sig")
    conseils = []
    texte = brut.strip()
    # Les ``` que Gemini met autour du code : on les tolère, et on le dit.
    if texte.startswith("```"):
        texte = re.sub(r"^```[a-zA-Z]*\s*", "", texte)
        texte = re.sub(r"\s*```\s*$", "", texte)
        conseils.append(("", "La fiche commence par ``` (la décoration de Gemini). Je l'ai ignorée ; "
                             "vous pouvez supprimer la première et la dernière ligne ```."))
    try:
        donnees = json.loads(texte)
    except json.JSONDecodeError as err:
        n, col, ligne, pointeur, probleme, a_faire = expliquer_json(err, texte)
        raise FicheInvalide({
            "titre": "%s n'est pas un JSON valide" % chemin.name,
            "ligne": n, "colonne": col, "extrait": ligne, "pointeur": pointeur,
            "probleme": probleme, "a_faire": a_faire,
        })
    return texte, donnees, conseils


def verifier_url(valeur, chemin, j, obligatoire=True):
    """Renvoie l'URL nettoyée, ou None (et note l'erreur)."""
    if valeur is None or (isinstance(valeur, str) and not valeur.strip()):
        if obligatoire:
            j.erreur(chemin, "l'adresse est vide.", 'écrivez une adresse complète, par exemple "https://www.linkedin.com/in/votre-nom"')
        return None
    if not isinstance(valeur, str):
        j.erreur(chemin, "l'adresse doit être un texte entre guillemets.", 'écrivez "%s": "https://…"' % chemin.split(".")[-1])
        return None
    u = valeur.strip()
    if re.search(r"\s", u):
        j.erreur(chemin, "l'adresse « %s » contient une espace." % u, "supprimez l'espace : une adresse web n'en contient jamais.")
        return None
    p = urlsplit(u)
    if p.scheme.lower() not in ("http", "https"):
        if not p.scheme and re.match(r"^(www\.)?[a-z0-9-]+(\.[a-z0-9-]+)+(/|$)", u, re.I):
            j.erreur(chemin, "« %s » n'est pas une adresse complète." % u, 'ajoutez https:// au début : "https://%s"' % u)
        else:
            j.erreur(chemin, "« %s » n'est pas une adresse web." % u, "une adresse commence par https:// (copiez-la depuis la barre d'adresse du navigateur).")
        return None
    hote = p.hostname or ""
    if "." not in hote or hote.startswith(".") or hote.endswith("."):
        j.erreur(chemin, "l'adresse « %s » n'a pas de nom de domaine valide." % u, "vérifiez-la en l'ouvrant dans votre navigateur, puis recopiez-la.")
        return None
    if p.scheme.lower() == "http":
        j.conseil(chemin, "« %s » commence par http:// : préférez https:// si le site l'accepte." % u)
    return u


def texte_requis(fiche, champ, j, obligatoire=True):
    v = fiche.get(champ)
    if v is None:
        if obligatoire:
            ex = EXEMPLES.get(champ, '"%s": "…",' % champ)
            j.erreur(champ, "ce champ obligatoire manque.", "ajoutez une ligne comme : %s" % ex)
        return None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        v = str(v)
    if not isinstance(v, str):
        j.erreur(champ, "la valeur doit être un texte entre guillemets.", "écrivez par exemple : %s" % EXEMPLES.get(champ, '"%s": "…",' % champ))
        return None
    v = v.strip()
    if not v:
        if obligatoire:
            j.erreur(champ, "le champ est vide.", "remplissez-le, par exemple : %s" % EXEMPLES.get(champ, '"%s": "…",' % champ))
        return None
    return v


def lister_textes(valeur, chemin, j):
    if isinstance(valeur, str):
        morceaux = [m.strip() for m in re.split(r"[,;]", valeur) if m.strip()]
        j.conseil(chemin, "« %s » devrait être une liste entre crochets ; je l'ai découpé aux virgules. "
                          "Écrivez plutôt : %s" % (chemin, json.dumps(morceaux, ensure_ascii=False)))
        return morceaux
    if not isinstance(valeur, list):
        j.erreur(chemin, "la valeur doit être une liste entre crochets.", 'écrivez par exemple : ["SEO", "Emailing"]')
        return []
    out = []
    for i, v in enumerate(valeur):
        if not isinstance(v, str) or not v.strip():
            j.erreur("%s[%d]" % (chemin, i), "chaque élément doit être un texte non vide entre guillemets.", 'écrivez par exemple : ["SEO", "Emailing"]')
            continue
        if v.strip() not in out:
            out.append(v.strip())
    return out


def normaliser_identifiant(v, j):
    if v is None:
        return None
    if not isinstance(v, str) or not v.strip():
        j.erreur("identifiant_github", "le champ est vide ou n'est pas un texte.", EXEMPLES["identifiant_github"])
        return None
    brut = v.strip()
    ident = brut.lstrip("@")
    m = re.match(r"^(?:https?://)?(?:www\.)?github\.com/([^/?#]+)", ident, re.I)
    if m:
        ident = m.group(1)
    m = re.match(r"^(?:https?://)?([^./]+)\.github\.io/?$", ident, re.I)
    if m:
        ident = m.group(1)
    if "@" in ident:
        j.erreur("identifiant_github", "« %s » ressemble à une adresse e-mail." % brut,
                 "écrivez votre identifiant GitHub (celui qui apparaît en haut à droite de GitHub, sans @).")
        return None
    if not re.match(r"^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$", ident):
        j.erreur("identifiant_github", "« %s » n'est pas un identifiant GitHub valide." % brut,
                 "un identifiant contient seulement des lettres, des chiffres et des tirets simples, par exemple marie-exemple.")
        return None
    if ident != brut:
        j.conseil("identifiant_github", "j'ai compris « %s » ; écrivez simplement \"identifiant_github\": \"%s\"." % (ident, ident))
    return ident


def lire_couleur(v, j):
    if v is None:
        j.conseil("couleur_accent", "pas de couleur d'accent : j'utilise %s (bleu encre)." % COULEUR_PAR_DEFAUT)
        return COULEUR_PAR_DEFAUT
    if not isinstance(v, str):
        j.erreur("couleur_accent", "la couleur doit être un texte entre guillemets.", EXEMPLES["couleur_accent"])
        return COULEUR_PAR_DEFAUT
    c = v.strip()
    if re.match(r"^[0-9a-fA-F]{6}$", c) or re.match(r"^[0-9a-fA-F]{3}$", c):
        c = "#" + c
    if re.match(r"^#[0-9a-fA-F]{3}$", c):
        c = "#" + "".join(ch * 2 for ch in c[1:])
    if not re.match(r"^#[0-9a-fA-F]{6}$", c):
        j.erreur("couleur_accent", "« %s » n'est pas une couleur au format #RRVVBB." % v,
                 'écrivez un code de six caractères après #, par exemple "#2952CC" (le Gem « Designer de ma page » en propose).')
        return COULEUR_PAR_DEFAUT
    return c.upper()


def lire_booleen(v, champ, j, defaut):
    if v is None:
        return defaut
    if isinstance(v, bool):
        return v
    if isinstance(v, str) and sans_accents(v.strip().lower()) in ("oui", "vrai", "true", "yes", "1"):
        j.conseil(champ, "écrivez true, sans guillemets (j'ai compris oui).")
        return True
    if isinstance(v, str) and sans_accents(v.strip().lower()) in ("non", "faux", "false", "no", "0"):
        j.conseil(champ, "écrivez false, sans guillemets (j'ai compris non).")
        return False
    j.erreur(champ, "la valeur doit être true ou false.", '"%s": true,  (ou false, sans guillemets)' % champ)
    return defaut


def nom_plateforme(url):
    hote = (urlsplit(url).hostname or "").lower()
    hote = re.sub(r"^(www\.|fr\.|m\.)", "", hote)
    for dom, nom in PLATEFORMES.items():
        if hote == dom or hote.endswith("." + dom):
            return nom
    return hote


def valider(fiche, j):
    """Vérifie la fiche et renvoie un dictionnaire propre (ou None si erreurs)."""
    if not isinstance(fiche, dict):
        j.erreur("", "la fiche doit être un objet entre accolades { … }.", "repartez de fiche.exemple.json.")
        return None

    # Champs inconnus : on les ignore, et on propose le bon nom.
    for cle in fiche:
        if cle.startswith("_") or cle.startswith("$"):
            continue  # les champs qui commencent par _ servent de commentaires
        if cle not in CHAMPS:
            proche = difflib.get_close_matches(cle, CHAMPS, n=1, cutoff=0.6)
            j.conseil(cle, "champ inconnu, ignoré.%s" % (" Vouliez-vous dire « %s » ?" % proche[0] if proche else ""))

    f = {}
    t = fiche.get("type", "Person")
    if t != "Person":
        j.erreur("type", "« %s » : pour ce TP, l'entité principale, c'est vous." % t,
                 'écrivez "type": "Person". Votre projet ou votre association va dans « entite_liee ».')
    f["type"] = "Person"

    for champ in ("nom", "phrase_identite", "metier", "ville"):
        f[champ] = texte_requis(fiche, champ, j)
    for champ in ("ce_que_je_fais", "parcours"):
        f[champ] = texte_requis(fiche, champ, j, obligatoire=False)

    if "domaines" not in fiche:
        j.erreur("domaines", "ce champ obligatoire manque.", "ajoutez : %s" % EXEMPLES["domaines"])
        f["domaines"] = []
    else:
        f["domaines"] = lister_textes(fiche["domaines"], "domaines", j)
        if not f["domaines"] and not j.erreurs:
            j.erreur("domaines", "la liste est vide.", "mettez au moins un domaine : %s" % EXEMPLES["domaines"])
        if len(f["domaines"]) > 10:
            j.conseil("domaines", "%d domaines : c'est beaucoup. Trois à six domaines précis disent mieux qui vous êtes." % len(f["domaines"]))

    # Employeur ou projet
    emp = fiche.get("employeur")
    if emp is None or emp == "" or emp == {}:
        f["employeur"] = None
        j.conseil("employeur", "pas d'employeur ni de projet : la propriété worksFor sera absente du JSON-LD.")
    else:
        if isinstance(emp, str):
            emp = {"nom": emp}
        if not isinstance(emp, dict):
            j.erreur("employeur", "la valeur doit être un objet entre accolades.", '"employeur": {"nom": "Lumen", "url": "https://lumen.example/"},')
            f["employeur"] = None
        else:
            nom = emp.get("nom")
            if not isinstance(nom, str) or not nom.strip():
                j.erreur("employeur.nom", "le nom de l'employeur ou du projet manque.", '"employeur": {"nom": "Lumen"},')
            for cle in emp:
                if cle not in ("nom", "url", "description", "libelle") and not cle.startswith("_"):
                    proche = difflib.get_close_matches(cle, ["nom", "url", "description", "libelle"], n=1)
                    j.conseil("employeur.%s" % cle, "champ inconnu, ignoré.%s" % (" Vouliez-vous dire « %s » ?" % proche[0] if proche else ""))
            f["employeur"] = {
                "nom": nom.strip() if isinstance(nom, str) else "",
                "url": verifier_url(emp.get("url"), "employeur.url", j, obligatoire=False),
                "description": (emp.get("description") or "").strip() if isinstance(emp.get("description", ""), str) else "",
                "libelle": (emp.get("libelle") or "Employeur").strip() if isinstance(emp.get("libelle", ""), str) else "Employeur",
            }

    # Profils ailleurs (sameAs)
    profils = fiche.get("profils", [])
    f["profils"] = []
    if isinstance(profils, dict):
        profils = [profils]
    if not isinstance(profils, list):
        j.erreur("profils", "la valeur doit être une liste entre crochets.", '"profils": [{"nom": "LinkedIn", "url": "https://www.linkedin.com/in/…"}],')
        profils = []
    vus = set()
    for i, p in enumerate(profils):
        chemin = "profils[%d]" % i
        if isinstance(p, str):
            p = {"url": p}
        if not isinstance(p, dict):
            j.erreur(chemin, "chaque profil doit être un objet {\"nom\": …, \"url\": …}.", '{"nom": "LinkedIn", "url": "https://www.linkedin.com/in/…"}')
            continue
        u = verifier_url(p.get("url"), chemin + ".url", j)
        if not u:
            continue
        nom = p.get("nom")
        if not isinstance(nom, str) or not nom.strip():
            nom = nom_plateforme(u)
            j.conseil(chemin, "pas de nom pour ce profil : j'affiche « %s »." % nom)
        if u.rstrip("/").lower() in vus:
            j.conseil(chemin, "ce profil apparaît deux fois ; je ne le garde qu'une fois.")
            continue
        vus.add(u.rstrip("/").lower())
        f["profils"].append({"nom": nom.strip(), "url": u})
    if not f["profils"] and not any(c.startswith("profils") for c, *_ in j.erreurs):
        j.conseil("profils", "aucun profil ailleurs : ajoutez au moins votre LinkedIn. C'est le sameAs, "
                             "la preuve que la page et le profil parlent de la même personne.")

    # Entité liée (bonus)
    f["entite_liee"] = None
    el = fiche.get("entite_liee")
    if el not in (None, "", {}):
        if not isinstance(el, dict):
            j.erreur("entite_liee", "la valeur doit être un objet entre accolades.", "voir l'exemple dans fiche.md, section entite_liee.")
        else:
            typ = el.get("type", "Organization")
            if typ not in ("Organization", "CreativeWork"):
                j.erreur("entite_liee.type", "« %s » n'est pas accepté ici." % typ,
                         'écrivez "Organization" (une association, une entreprise, un collectif) ou "CreativeWork" (un podcast, un blog, un livre, une œuvre).')
            nom = el.get("nom")
            if not isinstance(nom, str) or not nom.strip():
                j.erreur("entite_liee.nom", "le nom de l'entité liée manque.", '"nom": "Les Ateliers du mercredi",')
            rel = el.get("relation")
            prop = None
            if not isinstance(rel, str) or not rel.strip():
                j.erreur("entite_liee.relation", "la relation manque : quelle est votre place dans cette entité ?",
                         'écrivez par exemple "relation": "cofondatrice" (ou membre, bénévole, autrice, créatrice, contributrice).')
            else:
                r = sans_accents(rel.strip().lower())
                for debuts, p_, type_attendu, sens in RELATIONS:
                    if r.startswith(debuts):
                        prop = (p_, type_attendu, sens)
                        break
                if prop is None:
                    j.erreur("entite_liee.relation", "je ne sais pas traduire « %s » en schema.org." % rel,
                             "choisissez un de ces mots : fondatrice, cofondatrice, membre, bénévole, présidente (pour une Organization) ; "
                             "autrice, créatrice, contributrice (pour une CreativeWork). Le masculin marche aussi.")
                elif typ in ("Organization", "CreativeWork") and prop[1] != typ:
                    j.erreur("entite_liee.relation",
                             "« %s » ne va pas avec le type %s." % (rel, typ),
                             'changez le type en "%s", ou choisissez une relation adaptée à %s.' % (prop[1], typ))
            u = verifier_url(el.get("url"), "entite_liee.url", j, obligatoire=False)
            desc = el.get("description", "")
            titre = el.get("titre_section") or ("Mon projet" if typ == "Organization" else "Mon œuvre")
            if isinstance(nom, str) and nom.strip() and prop:
                f["entite_liee"] = {
                    "type": typ, "nom": nom.strip(), "url": u,
                    "description": desc.strip() if isinstance(desc, str) else "",
                    "relation": rel.strip(), "propriete": prop[0], "sens": prop[2],
                    "titre_section": titre.strip() if isinstance(titre, str) else "Mon projet",
                }

    theme = fiche.get("theme", "clair")
    if not isinstance(theme, str):
        theme = ""
    th = sans_accents(theme.strip().lower())
    if th not in THEMES:
        if "theme" in fiche:
            j.erreur("theme", "« %s » n'est pas un thème connu." % fiche.get("theme"),
                     'choisissez "clair", "sombre" ou "editorial".')
        th = "clair"
    f["theme"] = th
    f["couleur_accent"] = lire_couleur(fiche.get("couleur_accent"), j)
    f["animations"] = lire_booleen(fiche.get("animations"), "animations", j, True)
    f["fictif"] = lire_booleen(fiche.get("fictif"), "fictif", j, False)

    if "identifiant_github" not in fiche:
        j.erreur("identifiant_github", "ce champ obligatoire manque.", "ajoutez : %s" % EXEMPLES["identifiant_github"])
        f["identifiant_github"] = None
    else:
        f["identifiant_github"] = normaliser_identifiant(fiche.get("identifiant_github"), j)

    if j.erreurs:
        return None

    # Rien de privé : la page est publique.
    tout = json.dumps({k: v for k, v in fiche.items() if k != "verification_google"}, ensure_ascii=False)
    if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", tout):
        j.conseil("", "la fiche contient une adresse e-mail : elle sera publique. Gardez-la seulement si c'est voulu.")
    if re.search(r"(?<!\d)(?:\+33\s?|0)[1-9](?:[\s.-]?\d{2}){4}(?!\d)", tout):
        j.conseil("", "la fiche contient un numéro de téléphone : il sera public. Retirez-le si ce n'est pas voulu.")

    # Texte du modèle encore présent : un seul conseil par champ, et on s'arrête là.
    modele = False
    for champ in ("nom", "phrase_identite", "metier", "ville"):
        v = (f.get(champ) or "").casefold()
        if any(ph in v for ph in PLACEHOLDERS):
            j.conseil(champ, "contient encore le texte du modèle : remplacez-le par le vôtre.")
            modele = True
    if f["identifiant_github"] and f["identifiant_github"].lower() == "identifiant":
        j.conseil("identifiant_github", "vaut encore IDENTIFIANT : mettez votre identifiant GitHub.")
        modele = True
    if modele:
        return f

    # Conseils de cohérence : c'est l'idée du TP (dire la même chose partout).
    phrase = f["phrase_identite"].casefold()
    if f["nom"].casefold() not in phrase:
        j.conseil("phrase_identite", "votre phrase ne contient pas votre nom. « %s est … » aide les machines à relier la phrase à vous." % f["nom"])
    if f["ville"].casefold() not in phrase:
        j.conseil("phrase_identite", "votre phrase ne cite pas votre ville (%s). La répéter, c'est le NAP des entités." % f["ville"])
    if f["employeur"] and f["employeur"]["nom"] and f["employeur"]["nom"].casefold() not in phrase:
        j.conseil("phrase_identite", "votre phrase ne cite pas %s." % f["employeur"]["nom"])
    if len(f["phrase_identite"]) > 280:
        j.conseil("phrase_identite", "%d caractères : une phrase d'identité tient en une ou deux lignes (moins de 200 caractères)." % len(f["phrase_identite"]))

    return f


# ---------------------------------------------------------------------------
# Jour 2 (v2.1) : la photo, la vérification Google, les pages de contenu
# ---------------------------------------------------------------------------

PHOTO_MAX = 2 * 1024 * 1024
PHOTO_EXT = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WebP"}
RESERVES = {"index", "moi", "llms", "robots", "sitemap", "404", "polices"}
MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre")


def slugifier(s):
    s = sans_accents(str(s)).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-{2,}", "-", s)


def date_fr(iso):
    a, m, j_ = iso.split("-")
    j_ = int(j_)
    return "%s %s %s" % ("1er" if j_ == 1 else j_, MOIS[int(m) - 1], a)


def trouver_fichier(base, rel):
    """Le fichier tel qu'écrit, sinon le même nom sans tenir compte des majuscules."""
    p = (base / rel)
    if p.is_file():
        return p, False
    dossier = p.parent
    if dossier.is_dir():
        for x in dossier.iterdir():
            if x.is_file() and x.name.lower() == p.name.lower():
                return x, True
    return None, False


def fichiers_proches(base, rel, motif):
    noms = []
    for x in list(base.glob(motif)):
        try:
            noms.append(str(x.relative_to(base)).replace(os.sep, "/"))
        except ValueError:
            pass
    return difflib.get_close_matches(rel, noms, n=1, cutoff=0.5)


def lire_photo(v, j, base):
    """Renvoie {"fichier": Path ou None, "url": URL externe ou None, "nom_sortie": …}, ou None."""
    if v in (None, ""):
        return None
    if not isinstance(v, str):
        j.erreur("photo", "la valeur doit être un texte entre guillemets.", '"photo": "photo.jpg",')
        return None
    brut = v.strip()
    if re.match(r"^https?://", brut, re.I):
        u = verifier_url(brut, "photo", j)
        if not u:
            return None
        if urlsplit(u).scheme.lower() != "https":
            j.erreur("photo", "l'adresse de la photo commence par http://.", "utilisez une adresse en https://, ou envoyez la photo dans le dépôt.")
            return None
        if re.search(r"(linkedin|licdn|fbcdn|instagram)", u, re.I):
            j.conseil("photo", "une photo hébergée par LinkedIn ou Instagram change souvent d'adresse et peut disparaître : "
                               "envoyez plutôt le fichier dans le dépôt (Add file > Upload files).")
        return {"fichier": None, "url": u, "nom_sortie": None}
    rel = brut.lstrip("./").replace("\\", "/")
    ext = Path(rel).suffix.lower()
    if ext in (".heic", ".heif"):
        j.erreur("photo", "« %s » est au format HEIC (photo d'iPhone), que beaucoup de navigateurs n'affichent pas." % brut,
                 "ouvrez la photo et enregistrez-la en JPG (ou faites une capture d'écran), envoyez ce fichier, puis écrivez son nom ici.")
        return None
    if ext not in PHOTO_EXT:
        j.erreur("photo", "« %s » n'est pas une photo JPG, PNG ou WebP." % brut,
                 'écrivez le nom exact du fichier envoyé dans le dépôt, avec son extension, par exemple "photo.jpg".')
        return None
    p, casse = trouver_fichier(base, rel)
    if p is None:
        proche = fichiers_proches(base, rel, "*" + ext) or fichiers_proches(base, rel, "*.*")
        j.erreur("photo", "je ne trouve pas le fichier « %s » dans le dépôt." % brut,
                 "envoyez-le à la racine du dépôt (Add file > Upload files, puis Commit changes), "
                 "et recopiez ici son nom exact%s." % (" (vouliez-vous dire « %s » ?)" % proche[0] if proche else ""))
        return None
    if casse:
        j.conseil("photo", "le fichier s'appelle « %s » (majuscules différentes) : je l'utilise." % p.name)
    taille = p.stat().st_size
    if taille > PHOTO_MAX:
        j.erreur("photo", "« %s » pèse %.1f Mo : c'est trop lourd pour une page web (2 Mo au plus)." % (p.name, taille / 1048576),
                 "réduisez-la (une largeur de 800 pixels suffit), par exemple avec squoosh.app, puis renvoyez-la.")
        return None
    debut = p.read_bytes()[:12]
    signature = ("PNG" if debut.startswith(b"\x89PNG") else "JPEG" if debut.startswith(b"\xff\xd8")
                 else "WebP" if debut[:4] == b"RIFF" and debut[8:12] == b"WEBP" else None)
    if signature is None:
        j.erreur("photo", "« %s » n'est pas une image lisible (JPG, PNG ou WebP)." % p.name,
                 "renvoyez la photo depuis votre ordinateur, sans la renommer à la main.")
        return None
    if signature != PHOTO_EXT[ext]:
        j.conseil("photo", "« %s » est en réalité une image %s : elle s'affichera quand même." % (p.name, signature))
    nom = (slugifier(Path(p.name).stem) or "photo") + ext.replace(".jpeg", ".jpg")
    return {"fichier": p, "url": None, "nom_sortie": nom}


def lire_verification(v, j):
    if v in (None, ""):
        return None
    if not isinstance(v, str):
        j.erreur("verification_google", "la valeur doit être un texte entre guillemets.",
                 '"verification_google": "le code donné par Search Console",')
        return None
    brut = v.strip()
    if re.match(r"^google[0-9a-f]+\.html$", brut, re.I):
        j.erreur("verification_google", "« %s » est le nom d'un fichier : c'est la méthode « Fichier HTML »." % brut,
                 "dans Search Console, choisissez plutôt la méthode « Balise HTML », copiez la balise et collez-la ici.")
        return None
    m = re.search(r"content\s*=\s*[\"'“”]([^\"'“”]+)[\"'“”]", brut, re.I)
    code = m.group(1).strip() if m else brut
    if m:
        j.conseil("verification_google", "j'ai extrait le code de la balise ; vous pouvez n'écrire que \"%s\"." % code)
    if not re.match(r"^[A-Za-z0-9_\-]{10,100}$", code):
        j.erreur("verification_google", "je ne reconnais pas un code de vérification Google dans « %s »." % (brut[:80]),
                 "dans Search Console (méthode « Balise HTML »), copiez la balise entière <meta name=\"google-site-verification\" "
                 "content=\"…\"> ou seulement ce qu'il y a entre les guillemets après content=.")
        return None
    return code


def inline_md(texte, liens_pages, j, ou):
    """Échappe le texte, puis traduit [texte](adresse) et **gras**."""
    t = e(texte)

    def lien(m):
        etiquette, cible = m.group(1), html.unescape(m.group(2)).strip()
        bas = cible.lower()
        if bas.startswith(("javascript:", "data:", "vbscript:")):
            j.conseil(ou, "lien « %s » ignoré : adresse refusée." % cible)
            return etiquette
        cle = bas.lstrip("./")
        if cle.endswith(".md") and cle not in ("moi.md",):
            cle2 = cle if cle.startswith("pages/") else "pages/" + cle
            if cle in liens_pages or cle2 in liens_pages:
                cible = liens_pages.get(cle) or liens_pages[cle2]
            else:
                j.conseil(ou, "le lien vers « %s » ne mène à aucune page déclarée dans \"pages\" : "
                              "déclarez la page, ou corrigez le nom du fichier." % cible)
        elif not re.match(r"^(https?://|mailto:|#|/|\./|[\w\-]+\.(html|md|txt|xml)(#.*)?$)", cible, re.I):
            j.conseil(ou, "le lien « %s » n'est pas une adresse complète : ajoutez https:// au début." % cible)
        return '<a href="%s">%s</a>' % (e(cible), etiquette)

    t = re.sub(r"\[([^\]\n]+)\]\(\s*([^)\s]+)\s*\)", lien, t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    return t


def texte_brut_md(texte):
    t = re.sub(r"\[([^\]\n]+)\]\(\s*[^)\s]+\s*\)", r"\1", texte)
    return re.sub(r"\*\*(.+?)\*\*", r"\1", t).strip()


def lire_page_md(base, rel, i, j, nom_personne):
    """Lit pages/….md. Renvoie un dict, ou None (et note l'erreur)."""
    ou = "pages[%d]" % i
    if not isinstance(rel, str) or not rel.strip():
        j.erreur(ou, "chaque page doit être un nom de fichier entre guillemets.", '"pages": ["pages/ma-premiere-page.md"],')
        return None
    rel = rel.strip().lstrip("./").replace("\\", "/")
    if not rel.lower().endswith(".md"):
        j.erreur(ou, "« %s » ne finit pas par .md." % rel,
                 'une page est un fichier Markdown : nommez-le par exemple "pages/ma-premiere-page.md".')
        return None
    p, casse = trouver_fichier(base, rel)
    if p is None and not rel.startswith("pages/"):
        p, casse = trouver_fichier(base, "pages/" + rel)
    if p is None:
        proche = fichiers_proches(base, rel, "pages/*.md") or fichiers_proches(base, rel, "**/*.md")
        j.erreur(ou, "je ne trouve pas le fichier « %s » dans le dépôt." % rel,
                 "créez-le (Add file > Create new file, nom : %s), ou recopiez son nom exact%s. "
                 "Attention : majuscules, accents et espaces comptent." % (
                     rel, " (vouliez-vous dire « %s » ?)" % proche[0] if proche else ""))
        return None
    if casse:
        j.conseil(ou, "le fichier s'appelle « %s » (majuscules différentes) : je l'utilise." % p.name)
    try:
        lignes = p.read_text(encoding="utf-8-sig").splitlines()
    except UnicodeDecodeError:
        j.erreur(ou, "« %s » n'est pas enregistré en UTF-8." % rel,
                 "créez le fichier directement dans GitHub (Add file > Create new file) et collez-y le texte.")
        return None
    try:
        nom_affiche = str(p.relative_to(base)).replace(os.sep, "/")
    except ValueError:
        nom_affiche = rel
    k = 0
    while k < len(lignes) and not lignes[k].strip():
        k += 1
    m = re.match(r"^#\s+(.+?)\s*#*\s*$", lignes[k]) if k < len(lignes) else None
    if not m:
        vue = lignes[k].strip()[:60] if k < len(lignes) else "(fichier vide)"
        j.erreur(ou, "la première ligne de %s doit être le titre, précédé de # et d'une espace (j'y lis : « %s »)." % (nom_affiche, vue),
                 "écrivez en première ligne : # Le titre de ma page")
        return None
    titre = m.group(1).strip()
    k += 1
    while k < len(lignes) and not lignes[k].strip():
        k += 1
    date = None
    if k < len(lignes):
        md = re.match(r"^\s*(?:date|publi[ée]e? le)\s*:\s*(.+?)\s*$", lignes[k], re.I)
        if md:
            brute = md.group(1)
            iso = None
            m1 = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", brute)
            m2 = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", brute)
            if m1:
                a_, mo, jj = int(m1.group(1)), int(m1.group(2)), int(m1.group(3))
            elif m2:
                a_, mo, jj = int(m2.group(3)), int(m2.group(2)), int(m2.group(1))
            else:
                a_ = mo = jj = None
            if a_:
                try:
                    import datetime
                    iso = datetime.date(a_, mo, jj).isoformat()
                except ValueError:
                    iso = None
            if not iso:
                j.erreur(ou, "la date « %s » (ligne %d de %s) n'est pas une date valide." % (brute, k + 1, nom_affiche),
                         "écrivez par exemple : Date : 2026-11-04 (année-mois-jour) ou Date : 04/11/2026")
                return None
            date = iso
            k += 1
    corps = lignes[k:]
    blocs, courant = [], []
    for l in corps:
        if l.strip():
            courant.append(l.rstrip())
        elif courant:
            blocs.append(courant)
            courant = []
    if courant:
        blocs.append(courant)
    if not blocs:
        j.erreur(ou, "%s n'a pas de texte sous son titre." % nom_affiche,
                 "écrivez vos paragraphes sous le titre, séparés par une ligne vide.")
        return None
    texte_seul = " ".join(texte_brut_md(re.sub(r"^\s*(#+|[-*]|\d+[.)]|>)\s+", "", l)) for b in blocs for l in b)
    if nom_personne and nom_personne.casefold() not in texte_seul.casefold() and nom_personne.casefold() not in titre.casefold():
        j.conseil(ou, "votre nom (%s) n'apparaît pas dans %s : nommez-vous au moins une fois, « Marie Exemple a… » "
                      "plutôt que « j'ai… » (geste « Nommer »)." % (nom_personne, nom_affiche))
    if "[à sourcer]" in texte_seul.casefold() or "[a sourcer]" in sans_accents(texte_seul.casefold()):
        j.conseil(ou, "%s contient encore [À SOURCER] : une preuve manque. Ajoutez-la, ou retirez la phrase." % nom_affiche)
    nb_mots = len(texte_seul.split())
    if nb_mots < 80:
        j.conseil(ou, "%s ne fait que %d mot(s) : une page qui prouve en demande au moins 150 (un cas, une date, un résultat)." % (nom_affiche, nb_mots))
    if len(titre) > 110:
        j.conseil(ou, "le titre fait %d caractères : visez moins de 70, c'est le titre que Google affiche." % len(titre))
    slug = slugifier(Path(p.name).stem)
    if not slug:
        j.erreur(ou, "le nom du fichier « %s » ne donne pas d'adresse utilisable." % p.name,
                 "renommez-le avec des lettres et des tirets, par exemple pages/ma-premiere-page.md")
        return None
    if slug in RESERVES:
        j.erreur(ou, "« %s » donnerait l'adresse %s.html, réservée à la mallette." % (p.name, slug),
                 "renommez le fichier, par exemple pages/%s-article.md" % slug)
        return None
    return {"cle": nom_affiche.lower(), "fichier": nom_affiche, "titre": titre, "date": date, "blocs": blocs,
            "slug": slug, "texte_seul": texte_seul, "nb_mots": nb_mots}


def lire_pages(v, j, base, nom_personne):
    if v in (None, "", []):
        return []
    if isinstance(v, str):
        v = [v]
        j.conseil("pages", 'écrivez une liste entre crochets : "pages": ["%s"]' % v[0])
    if not isinstance(v, list):
        j.erreur("pages", "la valeur doit être une liste entre crochets.", '"pages": ["pages/ma-premiere-page.md"],')
        return []
    pages, slugs = [], {}
    for i, rel in enumerate(v):
        pg = lire_page_md(base, rel, i, j, nom_personne)
        if not pg:
            continue
        if pg["slug"] in slugs:
            j.erreur("pages[%d]" % i, "deux pages donneraient la même adresse %s.html (%s et %s)." % (
                pg["slug"], slugs[pg["slug"]], pg["fichier"]), "renommez l'un des deux fichiers, ou retirez le doublon de la liste.")
            continue
        slugs[pg["slug"]] = pg["fichier"]
        pages.append(pg)
    if len(pages) > 30:
        j.conseil("pages", "%d pages : c'est beaucoup pour une page d'entité. Gardez celles qui prouvent." % len(pages))
    return pages


def lire_extras(fiche, j, base, f):
    """Les trois champs du jour 2. Toujours appelée, pour montrer toutes les erreurs d'un coup."""
    if not isinstance(fiche, dict):
        return {"photo": None, "verification_google": None, "pages": []}
    nom = f["nom"] if f and f.get("nom") else (fiche.get("nom") if isinstance(fiche.get("nom"), str) else None)
    return {
        "photo": lire_photo(fiche.get("photo"), j, base),
        "verification_google": lire_verification(fiche.get("verification_google"), j),
        "pages": lire_pages(fiche.get("pages"), j, base, nom),
    }


def html_blocs(blocs, liens_pages, j, ou):
    """Les blocs Markdown d'une page, en HTML (paragraphes, ##, ###, listes, citations)."""
    L = []
    for b in blocs:
        tete = b[0]
        mh = re.match(r"^(#{1,3})\s+(.+?)\s*#*\s*$", tete)
        if mh:
            niveau = 3 if len(mh.group(1)) == 3 else 2
            if len(mh.group(1)) == 1:
                j.conseil(ou, "un seul # par page, pour le titre ; « # %s » devient un sous-titre ##." % mh.group(2))
            L.append("<h%d>%s</h%d>" % (niveau, inline_md(mh.group(2), liens_pages, j, ou), niveau))
            b = b[1:]
            if not b:
                continue
        if all(re.match(r"^\s*[-*]\s+", l) for l in b):
            L.append("<ul>")
            for l in b:
                L.append("  <li>%s</li>" % inline_md(re.sub(r"^\s*[-*]\s+", "", l), liens_pages, j, ou))
            L.append("</ul>")
        elif all(re.match(r"^\s*\d+[.)]\s+", l) for l in b):
            L.append("<ol>")
            for l in b:
                L.append("  <li>%s</li>" % inline_md(re.sub(r"^\s*\d+[.)]\s+", "", l), liens_pages, j, ou))
            L.append("</ol>")
        elif all(l.lstrip().startswith(">") for l in b):
            t = " ".join(re.sub(r"^\s*>\s?", "", l) for l in b)
            L.append("<blockquote><p>%s</p></blockquote>" % inline_md(t, liens_pages, j, ou))
        else:
            L.append("<p>%s</p>" % inline_md(" ".join(l.strip() for l in b), liens_pages, j, ou))
    return L


def premiere_phrase(pg, n=155):
    for b in pg["blocs"]:
        if re.match(r"^(#+|[-*]|\d+[.)])\s+", b[0]):
            continue
        t = texte_brut_md(" ".join(re.sub(r"^\s*>\s?", "", l).strip() for l in b))
        if len(t) <= n:
            return t
        coupe = t[:n].rsplit(" ", 1)[0]
        return coupe.rstrip(" ,;:") + "…"
    return pg["titre"]


EXTRA_CSS = """/* Mallette v2.1 (jour 2) : photo, « Mes pages », pages de contenu. Ajouté par construire.py. */
.photo { display: inline-block; line-height: 0; border-radius: 50%; }
.photo img {
  width: 6.5rem; height: 6.5rem; object-fit: cover; border-radius: 50%;
  border: 3px solid var(--accent); background: var(--ligne);
}
.pages-liste { list-style: none; margin: 0; padding: 0; }
.pages-liste li {
  display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between;
  gap: .15rem 1rem; padding: .7rem 0; border-top: 1px solid var(--ligne);
}
.pages-liste li:last-child { border-bottom: 1px solid var(--ligne); }
.pages-liste a { font-weight: 600; }
.pages-liste .date { color: var(--encre-3); font-size: .9rem; }
.fil { margin: 0 0 2.2rem; font-size: .95rem; color: var(--encre-3); max-width: none; }
.titre-article {
  margin: 0; font-family: var(--police-titre); font-weight: var(--graisse-titre, 700);
  font-stretch: var(--chasse-titre, 100%); font-size: clamp(2rem, 1.25rem + 3vw, 3.1rem);
  line-height: 1.08; letter-spacing: -.02em; text-wrap: balance;
}
.signature { margin: 0; color: var(--encre-2); font-size: 1rem; }
.texte h2 { margin: 2.2rem 0 .8rem; }
.texte h3 { margin: 1.6rem 0 .6rem; font-family: var(--police-titre); font-size: 1.1rem; }
.texte ul, .texte ol { margin: 0 0 .9em; padding-left: 1.3em; max-width: 38em; }
.texte li { margin: .25em 0; }
.texte blockquote { margin: 0 0 .9em; padding-left: 1rem; border-left: 3px solid var(--accent); color: var(--encre-2); }
.encart {
  display: flex; gap: 1rem; align-items: center; margin-top: 3rem; padding-top: 1.4rem;
  border-top: 1px solid var(--ligne-forte);
}
.encart .photo img { width: 3.6rem; height: 3.6rem; border-width: 2px; }
.encart p { margin: 0; }"""

EXTRA_MOUVEMENT = """@media (prefers-reduced-motion: no-preference) {
  .entete .photo { animation: m-pose .55s cubic-bezier(.2, .8, .2, 1) backwards; }
  .titre-article { animation: m-monte .8s cubic-bezier(.16, .84, .24, 1) .08s backwards; }
  .signature, .texte { animation: m-arrive .6s cubic-bezier(.2, .7, .2, 1) .5s backwards; }
}"""


# ---------------------------------------------------------------------------
# Les faits : la source unique de la page, du JSON-LD et de moi.md
# ---------------------------------------------------------------------------

def url_depuis_github():
    depot = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" not in depot:
        return None
    proprio, nom = depot.split("/", 1)
    hote = "%s.github.io" % proprio.lower()
    if nom.lower() == hote:
        return "https://%s/" % hote
    return "https://%s/%s/" % (hote, nom)


def faits(f, url_base):
    """Tout ce que la page affirme, une seule fois."""
    base = url_base if url_base.endswith("/") else url_base + "/"
    lignes = [("Métier", f["metier"])]
    if f["employeur"]:
        lignes.append((f["employeur"]["libelle"], f["employeur"]))
    lignes.append(("Ville", f["ville"]))
    lignes.append(("Domaines de compétence", f["domaines"]))
    photo = f.get("photo")
    photo_url = None
    if photo:
        photo_url = photo["url"] or base + photo["nom_sortie"]
    pages = []
    for pg in f.get("pages") or []:
        pages.append(dict(pg, url=base + pg["slug"] + ".html", url_md=base + pg["slug"] + ".md"))
    return {
        "url": base,
        "id": base + "#moi",
        "id_employeur": base + "#employeur",
        "id_liee": base + "#projet",
        "lignes": lignes,
        **f,
        "photo_url": photo_url,
        "pages": pages,
    }


def jsonld(F):
    """Le bloc schema.org. Chaque valeur ici est affichée sur la page."""
    p = {
        "@context": "https://schema.org",
        "@type": "Person",
        "@id": F["id"],
        "url": F["url"],
        "name": F["nom"],
        "description": F["phrase_identite"],
        "jobTitle": F["metier"],
    }
    if F.get("photo_url"):
        p["image"] = F["photo_url"]
    if F["employeur"]:
        org = {"@type": "Organization", "@id": F["id_employeur"], "name": F["employeur"]["nom"]}
        if F["employeur"]["url"]:
            org["url"] = F["employeur"]["url"]
        if F["employeur"]["description"]:
            org["description"] = F["employeur"]["description"]
        p["worksFor"] = org
    p["address"] = {"@type": "PostalAddress", "addressLocality": F["ville"]}
    p["knowsAbout"] = list(F["domaines"])
    if F["profils"]:
        p["sameAs"] = [x["url"] for x in F["profils"]]

    el = F["entite_liee"]
    if not el:
        return p
    # Bonus : deux entités reliées par leurs @id, dans un @graph.
    del p["@context"]
    autre = {"@type": el["type"], "@id": F["id_liee"], "name": el["nom"]}
    if el["description"]:
        autre["description"] = el["description"]
    if el["url"]:
        autre["url"] = el["url"]
    if el["propriete"] == "memberOf":
        p["memberOf"] = {"@id": F["id_liee"]}
    else:
        autre[el["propriete"]] = {"@id": F["id"]}
    return {"@context": "https://schema.org", "@graph": [p, autre]}


def phrase_fictif(F):
    """« Marie Exemple, Lumen et La Fournée n'existent pas »"""
    noms = [F["nom"]]
    if F["employeur"] and F["employeur"]["nom"]:
        noms.append(F["employeur"]["nom"])
    if F["entite_liee"]:
        noms.append(F["entite_liee"]["nom"])
    if len(noms) == 1:
        return "%s n'existe pas" % noms[0]
    return "%s et %s n'existent pas" % (", ".join(noms[:-1]), noms[-1])


def initiales(nom):
    mots = [m for m in re.split(r"[\s\-]+", nom) if m and m[0].isalnum()]
    if not mots:
        return "?"
    if len(mots) == 1:
        return mots[0][:2].upper()
    return (mots[0][0] + mots[-1][0]).upper()


def sans_schema(u):
    return re.sub(r"^https?://(www\.)?", "", u).rstrip("/")


# ---------------------------------------------------------------------------
# Fabrication des fichiers
# ---------------------------------------------------------------------------

def lire_theme(dossier_themes, theme):
    base = (dossier_themes / "base.css").read_text(encoding="utf-8")
    css_theme = (dossier_themes / ("%s.css" % theme)).read_text(encoding="utf-8")
    mouvement = (dossier_themes / "mouvement.css").read_text(encoding="utf-8")
    m = re.search(r"--fond:\s*(#[0-9a-fA-F]{6})", css_theme)
    fond = m.group(1).upper() if m else "#FFFFFF"
    polices = []
    for nom in re.findall(r'url\(["\']?polices/([^"\')]+)["\']?\)', css_theme):
        if nom not in polices:
            polices.append(nom)
    return base, css_theme, mouvement, fond, polices


def couleurs(accent, fond):
    texte = ajuster(accent, fond, 4.5)
    trait = ajuster(accent, fond, 3.0)
    blanc, nuit = "#FFFFFF", "#0E131C"
    sur = blanc if contraste(blanc, trait) >= contraste(nuit, trait) else nuit
    return {"accent": trait, "accent_texte": texte, "sur_accent": sur,
            "c_texte": contraste(texte, fond), "c_sur": contraste(sur, trait),
            "c_origine": contraste(accent, fond)}


def page_html(F, css, police_titre):
    L = []
    w = L.append
    titre = "%s – %s" % (F["nom"], F["metier"])
    bloc = json.dumps(jsonld(F), ensure_ascii=False, indent=2).replace("</", "<\\/")

    w("<!doctype html>")
    w('<html lang="fr">')
    w("<head>")
    w('<meta charset="utf-8">')
    w('<meta name="viewport" content="width=device-width, initial-scale=1">')
    w("<title>%s</title>" % e(titre))
    w('<meta name="description" content="%s">' % e(F["phrase_identite"]))
    if F["fictif"]:
        w('<meta name="robots" content="noindex">')
    if F.get("verification_google"):
        w('<meta name="google-site-verification" content="%s">' % e(F["verification_google"]))
    w('<link rel="canonical" href="%s">' % e(F["url"]))
    w('<link rel="alternate" type="text/markdown" href="moi.md" title="Cette page en Markdown">')
    w('<link rel="describedby" href="llms.txt" title="Sommaire pour les robots IA">')
    w('<meta property="og:type" content="profile">')
    w('<meta property="og:title" content="%s">' % e(F["nom"]))
    w('<meta property="og:description" content="%s">' % e(F["phrase_identite"]))
    w('<meta property="og:url" content="%s">' % e(F["url"]))
    w('<meta property="og:locale" content="fr_FR">')
    w('<meta name="generator" content="Mallette page d\'entité %s (outils/construire.py)">' % VERSION)
    if police_titre:
        w('<link rel="preload" href="polices/%s" as="font" type="font/woff2" crossorigin>' % e(police_titre))
    w("")
    w("<!-- La fiche d'identité pour les machines (schema.org, au format JSON-LD).")
    w("     Générée depuis fiche.json : chaque valeur ci-dessous est aussi écrite sur la page.")
    w("     Pour la changer, modifiez fiche.json, pas ce fichier. -->")
    w('<script type="application/ld+json">')
    w(bloc)
    w("</script>")
    w("")
    w("<style>")
    w(css)
    w("</style>")
    w("</head>")
    w("<body>")
    if F["fictif"]:
        w('<p class="bandeau" role="note"><strong>Exemple fictif.</strong> %s : '
          "cette page montre le résultat attendu du TP.</p>" % e(phrase_fictif(F)))
    w('<main class="page" id="contenu">')
    w('  <header class="entete">')
    if F.get("photo_url"):
        w('    <a class="photo" href="%s"><img src="%s" alt="%s" width="208" height="208"></a>' % (
            e(F["photo_url"]), e(F["photo"]["nom_sortie"] or F["photo_url"]), e(F["nom"])))
    else:
        w('    <span class="monogramme" aria-hidden="true">%s</span>' % e(initiales(F["nom"])))
    w('    <h1 class="nom"><span class="nom-texte">%s</span></h1>' % e(F["nom"]))
    w('    <span class="trait" aria-hidden="true"></span>')
    w('    <p class="phrase">%s</p>' % e(F["phrase_identite"]))
    w("  </header>")
    w("")
    w('  <div class="corps">')
    w('    <section class="fiche" aria-labelledby="t-bref">')
    w('      <h2 id="t-bref">En bref</h2>')
    w("      <dl>")
    for etiquette, valeur in F["lignes"]:
        if isinstance(valeur, dict):  # l'employeur
            nom = e(valeur["nom"])
            if valeur["url"]:
                nom = '<a href="%s">%s</a>' % (e(valeur["url"]), nom)
            if valeur["description"]:
                nom += ", %s" % e(valeur["description"])
            dd = nom
        elif isinstance(valeur, list):
            dd = '<ul class="domaines">%s</ul>' % "".join("<li>%s</li>" % e(v) for v in valeur)
        else:
            dd = e(valeur)
        w('        <div class="ligne"><dt>%s</dt><dd>%s</dd></div>' % (e(etiquette), dd))
    w("      </dl>")
    w("    </section>")
    for cle, titre_s, ident in (("ce_que_je_fais", "Ce que je fais", "t-fais"), ("parcours", "Parcours", "t-parcours")):
        if F.get(cle):
            w("")
            w('    <section aria-labelledby="%s">' % ident)
            w('      <h2 id="%s">%s</h2>' % (ident, titre_s))
            for para in couper_paragraphes(F[cle]):
                w("      <p>%s</p>" % e(para))
            w("    </section>")
    el = F["entite_liee"]
    if el:
        w("")
        w('    <section class="liee" aria-labelledby="t-liee">')
        w('      <h2 id="t-liee">%s</h2>' % e(el["titre_section"]))
        nom = e(el["nom"])
        if el["url"]:
            nom = '<a href="%s">%s</a>' % (e(el["url"]), nom)
        w("      <p>%s%s</p>" % (nom, (" : %s" % e(el["description"])) if el["description"] else ""))
        w('      <p>Mon rôle : <span class="relation">%s</span>.</p>' % e(el["relation"]))
        w("    </section>")
    if F.get("pages"):
        w("")
        w('    <section class="mes-pages" aria-labelledby="t-pages">')
        w('      <h2 id="t-pages">Mes pages</h2>')
        w('      <ul class="pages-liste">')
        for pg in F["pages"]:
            date = (' <span class="date"><time datetime="%s">%s</time></span>' % (pg["date"], date_fr(pg["date"]))
                    if pg["date"] else "")
            w('        <li><a href="%s.html">%s</a>%s</li>' % (e(pg["slug"]), e(pg["titre"]), date))
        w("      </ul>")
        w("    </section>")
    if F["profils"]:
        w("")
        w('    <section aria-labelledby="t-ailleurs">')
        w('      <h2 id="t-ailleurs">Me retrouver ailleurs</h2>')
        w('      <ul class="profils">')
        for p in F["profils"]:
            w('        <li><a href="%s" rel="me">%s</a> <span class="adresse">%s</span></li>' % (
                e(p["url"]), e(p["nom"]), e(sans_schema(p["url"]))))
        w("      </ul>")
        w("    </section>")
    w("  </div>")
    w("</main>")
    w("")
    w('<footer class="pied">')
    w('  <p>Adresse de cette page : <a href="%s">%s</a></p>' % (e(F["url"]), e(F["url"])))
    w('  <p>Pour les machines : cette page existe aussi en texte brut, <a href="moi.md">moi.md</a>, '
      'avec son sommaire, <a href="llms.txt">llms.txt</a>. Les faits de cette page sont aussi '
      "écrits dans son code, en données structurées schema.org.</p>")
    w('  <p class="credit">Page construite depuis une seule fiche (fiche.json) pendant le module SEO &amp; GEO '
      "du MBA MDIA, De Vinci Executive Education, novembre 2026.</p>")
    w("</footer>")
    w("</body>")
    w("</html>")
    return "\n".join(L) + "\n"


def moi_md(F):
    L = []
    w = L.append
    w("# %s" % F["nom"])
    w("")
    w("> %s" % F["phrase_identite"])
    w("")
    w("Page officielle : %s" % F["url"])
    w("")
    if F.get("photo_url"):
        w("Photo : %s" % F["photo_url"])
        w("")
    if F["fictif"]:
        w("Exemple fictif : %s." % phrase_fictif(F))
        w("")
    w("## En bref")
    w("")
    for etiquette, valeur in F["lignes"]:
        if isinstance(valeur, dict):
            t = valeur["nom"]
            if valeur["description"]:
                t += ", %s" % valeur["description"]
            if valeur["url"]:
                t += " (%s)" % valeur["url"]
        elif isinstance(valeur, list):
            t = ", ".join(valeur)
        else:
            t = valeur
        w("- %s : %s" % (etiquette, t))
    for cle, titre_s in (("ce_que_je_fais", "Ce que je fais"), ("parcours", "Parcours")):
        if F.get(cle):
            w("")
            w("## %s" % titre_s)
            for para in couper_paragraphes(F[cle]):
                w("")
                w(para)
    el = F["entite_liee"]
    if el:
        w("")
        w("## %s" % el["titre_section"])
        w("")
        w("- Nom : %s" % el["nom"])
        if el["description"]:
            w("- Description : %s" % el["description"])
        w("- Mon rôle : %s" % el["relation"])
        if el["url"]:
            w("- Adresse : %s" % el["url"])
    if F.get("pages"):
        w("")
        w("## Mes pages")
        w("")
        for pg in F["pages"]:
            w("- %s%s : %s (en Markdown : %s)" % (pg["titre"], (", %s" % date_fr(pg["date"])) if pg["date"] else "",
                                                 pg["url"], pg["url_md"]))
    if F["profils"]:
        w("")
        w("## Me retrouver ailleurs")
        w("")
        for p in F["profils"]:
            w("- %s : %s" % (p["nom"], p["url"]))
    w("")
    w("---")
    w("")
    w("Ce fichier est le jumeau Markdown de %s : les mêmes faits, mot pour mot. "
      "Il est généré depuis fiche.json, comme la page et ses données structurées." % F["url"])
    return "\n".join(L) + "\n"


def llms_txt(F):
    L = []
    w = L.append
    w("# %s" % F["nom"])
    w("")
    w("> %s" % F["phrase_identite"])
    w("")
    resume = "%s, %s" % (F["metier"], F["ville"])
    w("Ce site est la page d'entité de %s (%s). C'est la page de référence pour savoir qui est "
      "cette personne. La page HTML, son balisage schema.org (Person, @id %s) et la version Markdown "
      "disent exactement la même chose." % (F["nom"], resume, F["id"]))
    if F["fictif"]:
        w("")
        w("Exemple fictif : %s." % phrase_fictif(F))
    w("")
    w("## Pages")
    w("")
    w("- [Profil en Markdown](%smoi.md): tous les faits de la page, en texte brut" % F["url"])
    w("- [Page d'accueil](%s): la page de référence, avec ses données structurées schema.org" % F["url"])
    for pg in F.get("pages") or []:
        w("- [%s](%s): page de contenu signée par %s%s (en Markdown : %s)" % (
            pg["titre"], pg["url"], F["nom"], (", publiée le %s" % date_fr(pg["date"])) if pg["date"] else "", pg["url_md"]))
    if F["profils"]:
        w("")
        w("## Optional")
        w("")
        for p in F["profils"]:
            w("- [%s](%s): profil de %s sur %s" % (p["nom"], p["url"], F["nom"], nom_plateforme(p["url"])))
    return "\n".join(L) + "\n"


def jsonld_article(F, pg):
    """Le JSON-LD d'une page de contenu : un Article, signé par l'entité de la page d'accueil (#moi)."""
    a = {
        "@context": "https://schema.org",
        "@type": "Article",
        "@id": pg["url"] + "#article",
        "url": pg["url"],
        "mainEntityOfPage": pg["url"],
        "headline": pg["titre"],
        "description": premiere_phrase(pg),
        "inLanguage": "fr",
        "author": {"@type": "Person", "@id": F["id"], "name": F["nom"], "url": F["url"]},
    }
    if pg["date"]:
        a["datePublished"] = pg["date"]
    if F.get("photo_url"):
        a["author"]["image"] = F["photo_url"]
    return a


def page_article_html(F, pg, liens_pages, css, police_titre, j):
    L = []
    w = L.append
    ou = "pages[%d]" % pg["rang"]
    bloc = json.dumps(jsonld_article(F, pg), ensure_ascii=False, indent=2).replace("</", "<\\/")
    corps = html_blocs(pg["blocs"], liens_pages, j, ou)
    w("<!doctype html>")
    w('<html lang="fr">')
    w("<head>")
    w('<meta charset="utf-8">')
    w('<meta name="viewport" content="width=device-width, initial-scale=1">')
    w("<title>%s – %s</title>" % (e(pg["titre"]), e(F["nom"])))
    w('<meta name="description" content="%s">' % e(premiere_phrase(pg)))
    w('<meta name="author" content="%s">' % e(F["nom"]))
    if F["fictif"]:
        w('<meta name="robots" content="noindex">')
    w('<link rel="canonical" href="%s">' % e(pg["url"]))
    w('<link rel="alternate" type="text/markdown" href="%s.md" title="Cette page en Markdown">' % e(pg["slug"]))
    w('<meta property="og:type" content="article">')
    w('<meta property="og:title" content="%s">' % e(pg["titre"]))
    w('<meta property="og:description" content="%s">' % e(premiere_phrase(pg)))
    w('<meta property="og:url" content="%s">' % e(pg["url"]))
    w('<meta property="og:locale" content="fr_FR">')
    w('<meta name="generator" content="Mallette page d\'entité %s (outils/construire.py)">' % VERSION)
    if police_titre:
        w('<link rel="preload" href="polices/%s" as="font" type="font/woff2" crossorigin>' % e(police_titre))
    w("")
    w("<!-- Données structurées de cette page : un Article signé par l'entité")
    w("     de la page d'accueil (même @id). Générées depuis %s et fiche.json. -->" % e(pg["fichier"]))
    w('<script type="application/ld+json">')
    w(bloc)
    w("</script>")
    w("")
    w("<style>")
    w(css)
    w("</style>")
    w("</head>")
    w("<body>")
    if F["fictif"]:
        w('<p class="bandeau" role="note"><strong>Exemple fictif.</strong> %s : '
          "cette page montre le résultat attendu du TP.</p>" % e(phrase_fictif(F)))
    w('<main class="page article" id="contenu">')
    w('  <nav class="fil" aria-label="Fil d\'Ariane"><a href="%s">%s</a> › %s</nav>' % (
        e(F["url"]), e(F["nom"]), e(pg["titre"])))
    w('  <header class="entete">')
    w('    <h1 class="titre-article">%s</h1>' % e(pg["titre"]))
    w('    <span class="trait" aria-hidden="true"></span>')
    date = (', le <time datetime="%s">%s</time>' % (pg["date"], date_fr(pg["date"]))) if pg["date"] else ""
    w('    <p class="signature">Par <a href="%s" rel="author">%s</a>, %s%s</p>' % (
        e(F["url"]), e(F["nom"]), e(F["metier"][:1].lower() + F["metier"][1:]), date))
    w("  </header>")
    w("")
    w('  <article class="texte">')
    for ligne in corps:
        w("    " + ligne)
    w("  </article>")
    w("")
    w('  <aside class="encart" aria-label="Qui écrit cette page">')
    if F.get("photo_url"):
        w('    <a class="photo" href="%s"><img src="%s" alt="%s" width="116" height="116"></a>' % (
            e(F["url"]), e(F["photo"]["nom_sortie"] or F["photo_url"]), e(F["nom"])))
    else:
        w('    <span class="monogramme" aria-hidden="true">%s</span>' % e(initiales(F["nom"])))
    w('    <p>%s <a href="%s">Voir la page de %s</a>.</p>' % (e(F["phrase_identite"]), e(F["url"]), e(F["nom"])))
    w("  </aside>")
    autres = [x for x in F["pages"] if x["slug"] != pg["slug"]]
    if autres:
        w("")
        w('  <section class="mes-pages" aria-labelledby="t-autres">')
        w('    <h2 id="t-autres">Mes autres pages</h2>')
        w('    <ul class="pages-liste">')
        for x in autres:
            w('      <li><a href="%s.html">%s</a></li>' % (e(x["slug"]), e(x["titre"])))
        w("    </ul>")
        w("  </section>")
    w("</main>")
    w("")
    w('<footer class="pied">')
    w('  <p>Adresse de cette page : <a href="%s">%s</a></p>' % (e(pg["url"]), e(pg["url"])))
    w('  <p>Pour les machines : cette page existe aussi en texte brut, <a href="%s.md">%s.md</a>. '
      "Ses données structurées schema.org la relient à la page de %s.</p>" % (e(pg["slug"]), e(pg["slug"]), e(F["nom"])))
    w('  <p class="credit">Page construite depuis %s (et fiche.json) pendant le module SEO &amp; GEO '
      "du MBA MDIA, De Vinci Executive Education, novembre 2026.</p>" % e(pg["fichier"]))
    w("</footer>")
    w("</body>")
    w("</html>")
    return "\n".join(L) + "\n"


def article_md(F, pg, liens_abs):
    """Le jumeau Markdown d'une page de contenu : le même texte, avec qui l'a écrit."""
    L = ["# %s" % pg["titre"], ""]
    L.append("> Par %s (%s)%s." % (F["nom"], F["url"], (", le %s" % date_fr(pg["date"])) if pg["date"] else ""))
    L.append("")
    for b in pg["blocs"]:
        for l in b:
            def lien(m):
                cible = m.group(2).strip()
                cle = cible.lower().lstrip("./")
                cle2 = cle if cle.startswith("pages/") else "pages/" + cle
                return "[%s](%s)" % (m.group(1), liens_abs.get(cle) or liens_abs.get(cle2) or cible)
            L.append(re.sub(r"\[([^\]\n]+)\]\(\s*([^)\s]+)\s*\)", lien, l))
        L.append("")
    L.append("---")
    L.append("")
    L.append("Ce fichier est le jumeau Markdown de %s. Écrit par %s : %s" % (pg["url"], F["nom"], F["phrase_identite"]))
    return "\n".join(L) + "\n"


def robots_txt(F):
    return ("# robots.txt : qui peut lire ce site.\n"
            "# Tout le monde, y compris les robots des moteurs et des IA :\n"
            "# une page d'entité est faite pour être lue.\n"
            "User-agent: *\n"
            "Allow: /\n"
            "\n"
            "Sitemap: %ssitemap.xml\n" % F["url"])


def sitemap_xml(F):
    lignes = ["  <url><loc>%s</loc></url>" % html.escape(F["url"])]
    for pg in F.get("pages") or []:
        lm = "<lastmod>%s</lastmod>" % pg["date"] if pg["date"] else ""
        lignes.append("  <url><loc>%s</loc>%s</url>" % (html.escape(pg["url"]), lm))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(lignes) + "\n</urlset>\n")


def construire(f, url_base, sortie, dossier_themes, j=None):
    base, css_theme, mouvement, fond, polices = lire_theme(dossier_themes, f["theme"])
    c = couleurs(f["couleur_accent"], fond)
    variables = (":root {\n  --accent: %s;\n  --accent-texte: %s;\n  --sur-accent: %s;\n}\n"
                 % (c["accent"], c["accent_texte"], c["sur_accent"]))
    morceaux = [
        "/* Thème « %s », couleur d'accent %s. Généré par outils/construire.py. */" % (f["theme"], f["couleur_accent"]),
        base.strip(), css_theme.strip(),
    ]
    if f["animations"]:
        morceaux.append(mouvement.strip())
    if f.get("photo") or f.get("pages"):
        morceaux.append(EXTRA_CSS)
        if f["animations"]:
            morceaux.append(EXTRA_MOUVEMENT)
    morceaux.append("/* La couleur d'accent de fiche.json (ajustée si besoin pour rester lisible). */\n" + variables.strip())
    css = "\n\n".join(morceaux)

    F = faits(f, url_base)
    sortie.mkdir(parents=True, exist_ok=True)
    (sortie / "index.html").write_text(page_html(F, css, polices[0] if polices else None), encoding="utf-8")
    (sortie / "moi.md").write_text(moi_md(F), encoding="utf-8")
    (sortie / "llms.txt").write_text(llms_txt(F), encoding="utf-8")
    (sortie / "robots.txt").write_text(robots_txt(F), encoding="utf-8")
    (sortie / "sitemap.xml").write_text(sitemap_xml(F), encoding="utf-8")
    (sortie / ".nojekyll").write_text("", encoding="utf-8")

    if F.get("photo") and F["photo"]["fichier"]:
        shutil.copyfile(F["photo"]["fichier"], sortie / F["photo"]["nom_sortie"])
    liens_rel, liens_abs = {}, {}
    for pg in F["pages"]:
        for cle in (pg["cle"], pg["cle"].split("/")[-1]):
            liens_rel[cle] = pg["slug"] + ".html"
            liens_abs[cle] = pg["url"]
    for rang, pg in enumerate(F["pages"]):
        pg["rang"] = pg.get("rang_fiche", rang)
        (sortie / (pg["slug"] + ".html")).write_text(
            page_article_html(F, pg, liens_rel, css, polices[0] if polices else None, j), encoding="utf-8")
        (sortie / (pg["slug"] + ".md")).write_text(article_md(F, pg, liens_abs), encoding="utf-8")

    dossier_polices = sortie / "polices"
    if dossier_polices.exists():
        shutil.rmtree(dossier_polices)
    dossier_polices.mkdir()
    source = dossier_themes / "polices"
    for nom in polices:
        if (source / nom).exists():
            shutil.copyfile(source / nom, dossier_polices / nom)
            for lic in source.glob("OFL-*.txt"):
                if Path(nom).stem.startswith(lic.stem[4:]):
                    shutil.copyfile(lic, dossier_polices / lic.name)
    return F, c


# ---------------------------------------------------------------------------
# Affichage (terminal et GitHub Actions)
# ---------------------------------------------------------------------------

DANS_ACTIONS = os.environ.get("GITHUB_ACTIONS") == "true"


def annotation(niveau, titre, message, fichier=None, ligne=None):
    if not DANS_ACTIONS:
        return
    attrs = ["title=%s" % titre.replace(",", " ").replace("::", " ")]
    if fichier:
        attrs.insert(0, "file=%s" % fichier)
    if ligne:
        attrs.insert(1, "line=%d" % ligne)
    msg = message.replace("%", "%25").replace("\r", "").replace("\n", "%0A")
    print("::%s %s::%s" % (niveau, ",".join(attrs), msg))


def resume_actions(markdown):
    chemin = os.environ.get("GITHUB_STEP_SUMMARY")
    if chemin:
        with open(chemin, "a", encoding="utf-8") as fh:
            fh.write(markdown + "\n")


def afficher_json_invalide(d, nom_fichier):
    print()
    print("%s : la page n'a PAS été construite." % d["titre"])
    print()
    print("  Où       : ligne %d, colonne %d" % (d["ligne"], d["colonne"]))
    print("  Ligne %-3d: %s" % (d["ligne"], d["extrait"]))
    print("             %s" % d["pointeur"])
    print("  Problème : %s" % d["probleme"])
    print("  À faire  : %s" % d["a_faire"])
    print()
    print("Corrigez %s dans GitHub (crayon, puis Commit changes) : la page se reconstruira toute seule." % nom_fichier)
    annotation("error", "fiche.json n'est pas un JSON valide",
               "Ligne %d : %s À faire : %s" % (d["ligne"], d["probleme"], d["a_faire"]), nom_fichier, d["ligne"])
    resume_actions("## Votre fiche n'est pas un JSON valide\n\n"
                   "La page n'a pas été construite : votre ancienne page reste en ligne.\n\n"
                   "- **Où** : `%s`, ligne %d, colonne %d\n- **Ligne** : `%s`\n- **Problème** : %s\n- **À faire** : %s\n"
                   % (nom_fichier, d["ligne"], d["colonne"], d["extrait"].strip().replace("`", "'"), d["probleme"], d["a_faire"]))


def afficher_erreurs(j):
    n = len(j.erreurs)
    print()
    print("%s : %d erreur%s à corriger. La page n'a PAS été construite." % (j.fichier, n, "s" if n > 1 else ""))
    md = ["## Votre fiche est à corriger (%d erreur%s)" % (n, "s" if n > 1 else ""), "",
          "La page n'a pas été construite : votre ancienne page reste en ligne.", ""]
    for i, (chemin, probleme, a_faire, ligne) in enumerate(j.erreurs, 1):
        ou = "Champ %s" % joli_chemin(chemin) if chemin else "La fiche"
        if ligne:
            ou += " (ligne %d)" % ligne
        print()
        print("  %d. %s" % (i, ou))
        print("     Problème : %s" % probleme)
        print("     À faire  : %s" % a_faire)
        annotation("error", "Fiche à corriger : %s" % (chemin or "fiche"), "%s À faire : %s" % (probleme, a_faire), j.fichier, ligne)
        md.append("%d. **%s** : %s  \n   À faire : %s" % (i, ou, probleme, a_faire.replace("`", "'")))
    print()
    print("Corrigez %s (crayon, puis Commit changes) : la page se reconstruira toute seule." % j.fichier)
    resume_actions("\n".join(md))


def afficher_conseils(j):
    if not j.conseils:
        return []
    print()
    print("Conseils (rien de bloquant) :")
    out = []
    for chemin, texte in j.conseils:
        ou = ("%s : " % joli_chemin(chemin)) if chemin else ""
        print("  - %s%s" % (ou, texte))
        annotation("warning", "Conseil", "%s%s" % (ou, texte), j.fichier, j.ligne_de(chemin))
        out.append("- %s%s" % (ou, texte))
    return out


# ---------------------------------------------------------------------------
# Programme principal
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description="Construit la page d'entité depuis fiche.json.")
    ap.add_argument("--fiche", default=str(RACINE / "fiche.json"), help="la fiche à lire (défaut : fiche.json)")
    ap.add_argument("--sortie", default=str(RACINE / "_site"), help="le dossier à produire (défaut : _site)")
    ap.add_argument("--url-base", default=None, help="l'adresse de la page, par exemple https://marie.github.io/")
    ap.add_argument("--themes", default=str(RACINE / "themes"), help="le dossier des thèmes")
    a = ap.parse_args(argv)

    chemin = Path(a.fiche)
    if not chemin.is_absolute() and not chemin.exists():
        chemin = RACINE / chemin
    sortie = Path(a.sortie)
    if not sortie.is_absolute():
        sortie = Path.cwd() / sortie
    if sortie.resolve() == RACINE.resolve():
        print("Refusé : la sortie ne peut pas être la racine du dépôt (elle contient votre fiche).")
        return 2
    nom_fichier = chemin.name

    try:
        texte, donnees, conseils_lecture = lire_fiche(chemin)
    except FileNotFoundError:
        print("Introuvable : %s. Il doit être à la racine du dépôt, à côté de README.md." % chemin)
        annotation("error", "fiche.json introuvable", "Le fichier %s doit être à la racine du dépôt." % nom_fichier)
        resume_actions("## fiche.json introuvable\n\nLe fichier doit être à la racine du dépôt, à côté de README.md.")
        return 2
    except FicheInvalide as err:
        afficher_json_invalide(err.args[0], nom_fichier)
        return 1

    j = Journal(texte, nom_fichier)
    for chemin_c, t in conseils_lecture:
        j.conseil(chemin_c, t)
    f = valider(donnees, j)
    extras = lire_extras(donnees, j, chemin.parent, f)
    if f is None or j.erreurs:
        afficher_erreurs(j)
        afficher_conseils(j)
        return 1
    f.update(extras)

    url_base = a.url_base
    origine = "option --url-base"
    if not url_base:
        url_base = url_depuis_github()
        origine = "nom du dépôt GitHub"
        if url_base and f["identifiant_github"]:
            proprio = os.environ.get("GITHUB_REPOSITORY", "/").split("/")[0]
            if proprio.lower() != f["identifiant_github"].lower() and f["identifiant_github"].lower() != "identifiant":
                j.conseil("identifiant_github", "la fiche dit « %s », mais le dépôt appartient à « %s ». "
                                                "J'utilise « %s » pour l'adresse de la page." % (f["identifiant_github"], proprio, proprio))
            nom_depot = os.environ.get("GITHUB_REPOSITORY", "/").split("/", 1)[1]
            if nom_depot.lower() != ("%s.github.io" % proprio).lower():
                j.conseil("", "votre dépôt s'appelle « %s » : la page sera à %s. Pour l'adresse courte, "
                              "renommez le dépôt en %s.github.io (Settings, General, Repository name)." % (nom_depot, url_base, proprio.lower()))
    if not url_base:
        url_base = "https://%s.github.io/" % f["identifiant_github"].lower()
        origine = "identifiant_github de la fiche"
    if not re.match(r"^https?://[^/\s]+\.[^/\s]+", url_base):
        print("L'adresse « %s » n'est pas valide (exemple : https://marie.github.io/)." % url_base)
        return 2

    F, c = construire(f, url_base, sortie, Path(a.themes), j)

    if c["accent_texte"] != f["couleur_accent"]:
        j.conseil("couleur_accent", "%s n'a qu'un contraste de %.1f:1 sur le thème %s : trop faible pour du texte. "
                                    "Les liens utilisent %s (contraste %.1f:1, niveau AA)." % (
                                        f["couleur_accent"], c["c_origine"], f["theme"], c["accent_texte"], c["c_texte"]))

    try:
        affiche = sortie.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        affiche = sortie
    print("Page construite dans %s/ à partir de %s (mallette %s)." % (affiche, nom_fichier, VERSION))
    print()
    print("  Adresse       : %s   (d'après : %s)" % (F["url"], origine))
    print("  Identifiant   : %s" % F["id"])
    print("  Thème         : %s, accent %s, animations %s" % (f["theme"], f["couleur_accent"], "oui" if f["animations"] else "non"))
    print("  Contraste     : liens %.1f:1 sur le fond (AA demande 4,5:1)" % c["c_texte"])
    print("  Fichiers      : index.html, moi.md, llms.txt, robots.txt, sitemap.xml, .nojekyll, polices/")
    if F.get("photo_url"):
        print("  Photo         : %s" % F["photo_url"])
    if F.get("verification_google"):
        print("  Search Console: balise de vérification posée (google-site-verification)")
    for pg in F["pages"]:
        print("  Page          : %s  (%s, %d mots)" % (pg["url"], pg["fichier"], pg["nb_mots"]))
    conseils_md = afficher_conseils(j)
    print()
    print("Étape suivante : python3 outils/verifier.py%s" % ("" if sortie.name == "_site" else " %s" % affiche))
    annotation("notice", "Page construite", "Adresse : %s" % F["url"])
    extra_md = ""
    if F.get("photo_url"):
        extra_md += "- **Photo** : %s\n" % F["photo_url"]
    if F.get("verification_google"):
        extra_md += "- **Search Console** : balise de vérification posée ; retournez dans Search Console et cliquez sur Valider\n"
    for pg in F["pages"]:
        extra_md += "- **Page** : [%s](%s)\n" % (pg["titre"], pg["url"])
    resume_actions("## Page construite (mallette %s)\n\n- **Adresse** : %s\n- **Thème** : %s, accent `%s`, animations %s\n"
                   "- **Contraste des liens** : %.1f:1 (AA demande 4,5:1)\n%s%s"
                   % (VERSION, F["url"], f["theme"], f["couleur_accent"], "oui" if f["animations"] else "non", c["c_texte"],
                      extra_md,
                      ("\n### Conseils (rien de bloquant)\n\n" + "\n".join(conseils_md) + "\n") if conseils_md else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
