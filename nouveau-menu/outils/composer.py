#!/usr/bin/env python3
"""Compose le nouveau menu KING FOOD en HTML (A3 paysage, 4 colonnes par page),
dans la présentation de l'ancien menu imprimé : cartouches jaunes, plats numérotés,
descriptions en rouge, points de conduite jusqu'au prix.

    python3 outils/composer.py                    → menu-a-completer.html (menu + pages de questions)
    python3 outils/composer.py --sans-questions   → le menu seul
    python3 outils/composer.py --mesure           → une rubrique par colonne, pour mesurer.js

Le contenu vient de nouveau-menu.txt ; la répartition en colonnes est dans PLAN.
Les pages de questions destinées au restaurant sont décrites dans questions.py."""
import html
import pathlib
import re
import sys
import unicodedata

import questions

ICI = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ICI / "nouveau-menu.txt"
SORTIE = ICI / "menu-a-completer.html"
MENTION = "KING FOOD · Projet de nouveau menu · Version 2 · Prix à compléter · 26 novembre 2026"

# Répartition : 4 colonnes par page. ("section", titre) place une rubrique entière ;
# ("section", titre, début, fin) n'en place qu'une tranche de plats (la suite porte « (suite) »).
# Les blocs « deco » sont élastiques : ils occupent la hauteur laissée libre dans leur colonne.
PLAN = [
    # page 1 — petits déjeuners, entrées, sandwichs
    [("tete",), ("section", "Petit déjeuner"), ("section", "Petit déjeuner oriental"), ("deco", "tasse", "a")],
    [("section", "Nos entrées froides"), ("deco", "salade", "b")],
    [("section", "Entrées chaudes"), ("deco", "soupe", "c")],
    [("section", "Sandwichs"), ("section", "Chawarmas", 0, 7)],
    # page 2 — chawarmas, burgers, pizzas
    [("section", "Chawarmas", 7, None), ("deco", "frites", "a")],
    [("section", "Burgers")],
    [("section", "Pizzas", 0, 16)],
    [("section", "Pizzas", 16, None)],
    # page 3 — plats, menu enfants, desserts
    [("section", "Nos pâtes"), ("section", "Fruits de mer"), ("section", "Menu enfants")],
    [("section", "Viandes rouges"), ("section", "Brochettes & grillades"), ("deco", "brochette", "c")],
    [("section", "Viandes blanches"), ("section", "Nouveautés du chef"), ("deco", "toque", "a")],
    [("section", "Crêpes"), ("section", "Gaufres"), ("section", "Gâteaux"), ("section", "Glaces"), ("deco", "glace", "b")],
    # page 4 — cocktails, jus, boissons, chicha
    [("section", "Cocktails", 0, 18)],
    [("section", "Cocktails", 18, None), ("deco", "verre", "c")],
    [("section", "Jus nature"), ("section", "Jus mixte"), ("section", "Boissons chaudes"), ("deco", "tasse", "a")],
    [("section", "Boissons"), ("section", "Chicha"), ("deco", "bouteille", "b")],
]

J, R, N = "#FDC40F", "#C8393B", "#111111"   # jaune, rouge, noir de la charte

# Pictogrammes (viewBox 0 0 100 100), dessinés au trait dans les couleurs de la charte.
ICONES = {
    "tasse": f'<path d="M27 47h40v12a20 20 0 0 1-40 0z" fill="{J}"/><path d="M67 51h4a8 8 0 0 1 0 16h-6"/>'
             f'<path d="M22 85h50"/><path d="M39 37c-5-6 5-9 0-15M49 37c-5-6 5-9 0-15M59 37c-5-6 5-9 0-15" stroke="{R}"/>',
    "salade": f'<path d="M28 54c-6-12 6-22 14-16c2-12 18-12 20-2c10-6 18 6 12 18z" fill="{J}"/>'
              f'<circle cx="42" cy="46" r="5" fill="{R}"/><circle cx="59" cy="45" r="5" fill="{R}"/>'
              f'<path d="M16 54h68a34 30 0 0 1-68 0z" fill="#fff"/><path d="M30 68h40" stroke="{J}"/><path d="M38 86h24"/>',
    "soupe": f'<path d="M64 50L82 22" stroke-width="4.5"/><path d="M16 50h68a34 32 0 0 1-68 0z" fill="{J}"/><path d="M11 50h78"/>'
             f'<path d="M36 85h28"/><path d="M34 40c-5-6 5-9 0-16M46 40c-5-6 5-9 0-16M58 40c-5-6 5-9 0-16" stroke="{R}"/>',
    "burger": f'<path d="M20 46a30 24 0 0 1 60 0z" fill="{J}"/><path d="M36 36l3-2M50 31l3-2M62 37l3-2M45 41l3-2" stroke-width="2.4"/>'
              f'<path d="M18 52q5.3 7 10.6 0t10.6 0t10.6 0t10.6 0t10.6 0t10.6 0" stroke="{R}"/>'
              f'<rect x="20" y="58" width="60" height="10" rx="5" fill="{N}"/><path d="M22 74h56v3a8 8 0 0 1-8 8H30a8 8 0 0 1-8-8z" fill="{J}"/>',
    "pates": f'<path d="M22 54c2-18 54-18 56 0z" fill="{J}"/><path d="M32 52c3-10 33-10 36 0M42 52c2-6 14-6 16 0" stroke-width="2.4"/>'
             f'<path d="M14 54h72a36 30 0 0 1-72 0z" fill="#fff"/><path d="M36 85h28"/>'
             f'<path d="M66 10v13M72 10v13M78 10v13M66 23q6 6 12 0M72 26L65 42" stroke-width="2.6"/>',
    "poisson": f'<path d="M16 52c12-20 40-20 54 0c-14 20-42 20-54 0z" fill="{J}"/><path d="M70 52l16-13l-4 13l4 13z" fill="{J}"/>'
               f'<circle cx="30" cy="48" r="2.8" fill="{N}" stroke="none"/><path d="M41 40c5 7 5 17 0 24"/>'
               f'<path d="M50 46c3 4 3 8 0 12M58 47c2 3 2 7 0 10" stroke-width="2.4"/>'
               f'<circle cx="24" cy="25" r="3.2" stroke="{R}"/><circle cx="34" cy="16" r="2.2" stroke="{R}"/>',
    "frites": f'<path d="M40 52l-4-26h7l3 26zM48 52V20h7v32zM56 52l5-28h7l-6 28z" fill="{J}"/>'
              f'<path d="M30 50h40l-7 36H37z" fill="{R}"/><path d="M37 63h26" stroke="#fff"/>',
    "brochette": f'<g transform="rotate(-40 50 50)"><path d="M2 50h96"/><circle cx="7" cy="50" r="5" fill="#fff"/>'
                 f'<rect x="24" y="39" width="15" height="22" rx="4" fill="{J}"/><rect x="43" y="39" width="15" height="22" rx="4" fill="{R}"/>'
                 f'<rect x="62" y="39" width="15" height="22" rx="4" fill="{J}"/></g>',
    "pilon": f'<path d="M46 58L27 77" stroke-width="10"/><path d="M46 58L27 77" stroke="#fff" stroke-width="4.4"/>'
             f'<circle cx="22" cy="76" r="5.5" fill="#fff"/><circle cx="28" cy="82" r="5.5" fill="#fff"/>'
             f'<ellipse cx="60" cy="42" rx="25" ry="19" transform="rotate(-38 60 42)" fill="{J}"/><path d="M54 32c6-5 15-5 21 1" stroke-width="2.4"/>',
    "steak": f'<path d="M20 46c0-18 22-26 38-20c16-6 30 10 24 28c-4 16-24 26-42 20c-12-4-20-14-20-28z" fill="{R}"/>'
             f'<path d="M36 46c6-8 16-8 22-1M40 60c8 6 20 4 26-4" stroke="#fff" stroke-width="2.8"/><circle cx="66" cy="40" r="5" fill="#fff"/>',
    "glace": f'<path d="M35 48L50 90L65 48z" fill="{J}"/><path d="M41 60l15-9M46 72l11-7" stroke-width="2.4"/>'
             f'<circle cx="50" cy="34" r="18" fill="#fff"/><path d="M38 30c5-8 19-8 24 0" stroke="{R}"/><circle cx="50" cy="12" r="4.5" fill="{R}"/>',
    "bouteille": f'<path d="M44 12h12v14c0 8 10 10 10 22v36a4 4 0 0 1-4 4H38a4 4 0 0 1-4-4V48c0-12 10-14 10-22z" fill="{J}"/>'
                 f'<path d="M34 56h32v16H34z" fill="#fff"/><path d="M43 11h14" stroke="{R}" stroke-width="5"/>',
    "pizza": f'<path d="M50 88L18 30q32-18 64 0z" fill="{J}"/><path d="M18 30q32-18 64 0" stroke-width="5.5"/>'
             f'<circle cx="41" cy="42" r="5.5" fill="{R}"/><circle cx="59" cy="46" r="5.5" fill="{R}"/><circle cx="50" cy="64" r="5" fill="{R}"/>',
    "verre": f'<path d="M27 24h46L50 54z" fill="{J}"/><path d="M50 54v28M36 86h28"/><path d="M58 34L78 10" stroke="{R}"/>'
             f'<circle cx="41" cy="33" r="4.5" fill="{R}"/>',
    "gateau": f'<path d="M31 54h38l-6 32H37z" fill="{J}"/><path d="M41 60v20M50 60v20M59 60v20" stroke-width="2.2"/>'
              f'<path d="M27 54c-5-13 6-22 15-18c3-12 23-11 23 2c10-2 13 9 9 16z" fill="#fff"/><circle cx="50" cy="19" r="4.6" fill="{R}"/>',
    "toque": f'<path d="M30 58c-16-2-16-24 0-26c2-14 22-16 28-4c12-8 28 6 16 22c-1 3-4 6-4 8v20H30z" fill="#fff"/>'
             f'<path d="M30 64h40v14H30z" fill="{J}"/><path d="M42 46v12M50 44v14M58 46v12" stroke-width="2.4"/>',
}

FLECHE = (f'<svg class="fleche" viewBox="0 0 100 60"><g fill="none" stroke="{J}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">'
          '<path d="M6 52C22 16 60 6 90 26"/><path d="M90 26l-21-2M90 26l-7-20"/></g></svg>')
ZIGZAG = (f'<svg class="zig" viewBox="0 0 12 70"><path d="M2 2l8 6l-8 6l8 6l-8 6l8 6l-8 6l8 6l-8 6l8 6l-8 6" fill="none" stroke="{N}" '
          'stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/></svg>')
ARCS = (f'<svg class="arcs" viewBox="0 0 100 100"><g fill="none" stroke="{J}" stroke-width="3.2">'
        '<circle cx="50" cy="50" r="46"/><circle cx="50" cy="50" r="36"/><circle cx="50" cy="50" r="26"/></g></svg>')
GRIBOUILLIS = (f'<svg class="gribouillis" viewBox="0 0 100 100"><g fill="none" stroke="{N}" stroke-width="1.6">'
               '<ellipse cx="50" cy="50" rx="47" ry="45" transform="rotate(-12 50 50)"/><ellipse cx="50" cy="50" rx="46" ry="48" transform="rotate(20 50 50)"/>'
               '<ellipse cx="51" cy="49" rx="48" ry="44" transform="rotate(48 50 50)"/></g></svg>')


def slug(texte):
    t = unicodedata.normalize("NFD", texte)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def lire(source):
    """nouveau-menu.txt → liste de rubriques ; les plats sont numérotés dans l'ordre du fichier."""
    rubriques, numero, cles = [], 0, set()
    for n, brut in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
        ligne = brut.strip()
        if not ligne or ligne.startswith("//"):
            continue
        champs = [c.strip() for c in ligne.lstrip("#").split("|")]
        if ligne.startswith("##"):
            r = {"titre": champs[0], "note": "", "formats": [], "plats": []}
            for c in champs[1:]:
                if c.startswith("@"):
                    r["formats"] = [f.strip() for f in c[1:].split("/")]
                elif c:
                    r["note"] = c
            rubriques.append(r)
            continue
        if not rubriques or not champs[0]:
            raise SystemExit(f"nouveau-menu.txt, ligne {n} : plat sans rubrique ou sans nom")
        champs += [""] * (4 - len(champs))
        numero += 1
        r = rubriques[-1]
        # « cle » identifie le plat indépendamment de son numéro : elle nomme les champs du PDF
        plat = {"num": numero, "nom": champs[0], "desc": champs[1], "formats": [], "prix": champs[2],
                "cle": f'{slug(r["titre"])}__{slug(champs[0])}'}
        if champs[2].startswith("@"):
            plat["formats"] = [f.strip() for f in champs[2][1:].split("/")]
            plat["prix"] = champs[3]
        if plat["cle"] in cles:
            raise SystemExit(f"nouveau-menu.txt, ligne {n} : « {champs[0]} » figure deux fois dans « {r['titre']} »")
        cles.add(plat["cle"])
        r["plats"].append(plat)
    return rubriques


def case_prix(plat, fmt, valeur):
    """Le prix s'il est connu, sinon une case vide (qui deviendra un champ de saisie dans le PDF)."""
    e = html.escape
    if valeur:
        return f'<span class="prix">{e(valeur)}&nbsp;F</span>'
    nom = f'prix__{plat["cle"]}' + (f'__{slug(fmt)}' if fmt else "")
    libelle = f'Prix du n° {plat["num"]} — {plat["nom"]}' + (f' ({fmt})' if fmt else "")
    return (f'<span class="prix"><span class="blanc" data-champ="{nom}" data-libelle="{e(libelle, quote=True)}"></span>'
            '<span class="f">F</span></span>')


def prix_par_format(plat, formats):
    prix = [x.strip() for x in plat["prix"].split("/")] if plat["prix"] else []
    return prix + [""] * (len(formats) - len(prix))


def rendu_plat(p, formats_rubrique=()):
    e = html.escape
    nom = f'<span class="nom"><span class="num">{p["num"]}&nbsp;-</span> {e(p["nom"])}</span>'
    if formats_rubrique:                      # deux colonnes de prix, alignées sous les en-têtes de la rubrique
        prix = prix_par_format(p, formats_rubrique)
        cellules = "".join(f'<span class="cellule">{case_prix(p, f, prix[i])}</span>' for i, f in enumerate(formats_rubrique))
        corps = f'<div class="ligne">{nom}<span class="suite double"><span class="points"></span>{cellules}</span></div>'
    elif p["formats"]:                        # deux prix pour ce seul plat, sur une ligne à part
        prix = prix_par_format(p, p["formats"])
        formats = "".join(
            f'<span class="fmt"><span class="fmt-nom">{e(f)}</span><span class="points"></span>{case_prix(p, f, prix[i])}</span>'
            for i, f in enumerate(p["formats"]))
        corps = f'<div class="ligne">{nom}</div><div class="formats">{formats}</div>'
    else:
        corps = f'<div class="ligne">{nom}<span class="suite"><span class="points"></span>{case_prix(p, None, p["prix"])}</span></div>'
    if p["desc"]:
        corps += f'<div class="desc">({e(p["desc"])})</div>'
    return f'<div class="plat">{corps}</div>'


def rendu_section(r, debut=0, fin=None):
    """Une rubrique, ou la tranche [debut:fin] de ses plats (la suite d'une rubrique répartie sur deux colonnes)."""
    e = html.escape
    libelle = r["titre"] + (" (suite)" if debut else "")
    if slug(r["titre"]) == "menu-enfants":      # pastille rouge, comme sur l'ancien menu
        mots = e(r["titre"]).upper().split(" ", 1)
        titre = (f'<div class="titre-enfants"><div class="pastille">{GRIBOUILLIS}<span>{mots[0]}<br>{mots[1]}</span></div></div>')
    else:
        titre = f'<h2 class="titre"><span>{e(libelle)}</span></h2>'
    note = f'<p class="note-rubrique">{e(r["note"])}</p>' if r["note"] and not debut else ""
    entetes = ('<div class="entetes">' + "".join(f"<span>{e(f)}</span>" for f in r["formats"]) + '</div>') if r["formats"] else ""
    plats = "".join(rendu_plat(p, r["formats"]) for p in r["plats"][debut:fin])
    ident = slug(r["titre"]) + (f"-{debut}" if debut else "")
    return (f'<section class="rubrique" id="{ident}" data-titre="{e(r["titre"], quote=True)}">{titre}{note}{entetes}'
            f'<div class="plats">{plats}</div></section>')


def rendu_deco(icone, variante):
    return (f'<div class="deco deco-{variante}"><div class="scene">{ARCS}{FLECHE}{ZIGZAG}<span class="pois"></span><span class="trois"><i></i><i></i><i></i></span>'
            f'<div class="disque"><svg viewBox="0 0 100 100"><g fill="none" stroke="{N}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">'
            f'{ICONES[icone]}</g></svg></div></div></div>')


TETE = ('<div class="tete"><img src="../qr/logo-hd.png" alt=""><div class="tete-kicker">Le menu</div>'
        '<div class="tete-nom">King Food</div><div class="tete-devise">Vous êtes entre de bonnes mains</div></div>')

CSS = """
:root{--jaune:#FDC40F;--rouge:#C8393B;--noir:#111;--marine:#2B2D4E;
  --plat:13.3pt;--desc:10.6pt;--titre:42pt;--bandeau:16mm}
@page{size:420mm 297mm;margin:0}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#fff}
body{font-family:'KF Texte',Arial,sans-serif;color:var(--noir);-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{position:relative;width:420mm;height:297mm;overflow:hidden;page-break-after:always;background:#fff}
.page:last-child{page-break-after:auto}

/* Cadre marine + filet jaune décalé, comme sur l'ancien menu */
.filet-jaune{position:absolute;left:13.5mm;top:13.5mm;right:7.5mm;bottom:8.5mm;border-right:1.1mm solid var(--jaune);border-bottom:1.1mm solid var(--jaune)}
.cadre{position:absolute;left:10mm;top:10mm;right:11mm;bottom:12mm;border:1.3mm solid var(--marine);background:#fff;
  display:grid;grid-template-columns:repeat(4,1fr)}
.col{position:relative;min-width:0;min-height:0;display:flex;flex-direction:column;overflow:hidden;padding:0 4mm 2.5mm}
.col + .col{border-left:1.1mm solid var(--noir)}
.mention{position:absolute;left:10mm;bottom:3.4mm;font-size:7.6pt;color:#777;letter-spacing:.02em}
.folio{position:absolute;right:11mm;bottom:3.4mm;font-size:7.6pt;color:#777}

/* Cartouche de rubrique : bandeau jaune pleine colonne, capitales manuscrites */
.rubrique{flex:0 0 auto}
.titre{margin:0 -4mm 2.6mm;height:var(--bandeau);background:var(--jaune);display:flex;align-items:center;justify-content:center;
  font-family:'KF Titre',sans-serif;font-weight:700;font-size:var(--titre);line-height:1;text-transform:uppercase;letter-spacing:.045em;
  -webkit-text-stroke:.42mm var(--noir);white-space:nowrap;overflow:hidden}
.titre span{display:inline-block;transform:translateY(-.2mm)}
.rubrique + .rubrique .titre, .deco + .rubrique .titre{margin-top:1mm}

/* Pastille rouge du menu enfants */
.titre-enfants{display:flex;justify-content:center;margin:1mm 0 2mm}
.pastille{position:relative;width:40mm;height:40mm;border-radius:50%;background:var(--rouge);display:grid;place-items:center}
.pastille span{font-family:'KF Titre',sans-serif;font-weight:700;font-size:32pt;line-height:.9;color:#fff;text-align:center;text-transform:uppercase;
  letter-spacing:.05em;-webkit-text-stroke:.34mm #fff}
.pastille .gribouillis{position:absolute;inset:-2.2mm;width:auto;height:auto}

/* Plats : « 12 - Nom ........ prix F », description en rouge entre parenthèses */
.plat{padding:.72mm 0;break-inside:avoid}
.ligne{display:flex;flex-wrap:wrap;align-items:flex-end;font-size:var(--plat);font-weight:700;line-height:1.22}
.nom{flex:0 1 auto;min-width:0;max-width:100%}
.num{white-space:nowrap}
/* Nom trop long : la suite (points + prix) passe seule à la ligne suivante, en retrait — comme sur l'ancien menu */
.suite{flex:1 1 22.5mm;min-width:22.5mm;display:flex;align-items:flex-end}
.suite.a-la-ligne{margin-left:8.5mm;padding-top:.4mm}
.points{flex:1 1 3mm;min-width:3mm;margin:0 1.1mm .34em;border-bottom:.55mm dotted var(--noir)}
.prix{flex:0 0 auto;white-space:nowrap;font-weight:700;display:inline-flex;align-items:flex-end}
.blanc{display:inline-block;width:13.5mm;height:5.4mm;margin-right:1mm;border-bottom:.25mm solid #9a9a9a}
.desc{margin:.15mm 0 0 8.5mm;font-size:var(--desc);line-height:1.2;color:var(--rouge);font-weight:400}
.formats{display:flex;gap:4mm;margin:.6mm 0 .4mm 7mm;font-size:calc(var(--plat) - 1.2pt);font-weight:700}
.fmt{flex:1;display:flex;align-items:flex-end;min-width:0}
.fmt-nom{font-family:'KF Script',cursive;font-weight:400;font-size:18pt;line-height:.9;transform:translateY(.7mm)}
.fmt .points{flex-basis:3mm;min-width:3mm}
.fmt .blanc{width:11.5mm}

/* Note sous le titre d'une rubrique */
.note-rubrique{margin:-.8mm 0 1.4mm;font-size:10.2pt;line-height:1.28;color:#444;font-style:italic;text-align:center}

/* Rubrique à deux colonnes de prix (burgers : sandwich / assiette ; pizzas : petite / grande) */
:root{--cell:17.4mm;--ecart:1.2mm}
.entetes{display:flex;justify-content:flex-end;gap:var(--ecart);margin:-.4mm 0 .2mm;font-size:8.4pt;font-weight:700;
  text-transform:uppercase;letter-spacing:.04em;color:#555}
.entetes span{flex:0 0 var(--cell);text-align:center}
.suite.double{flex-basis:calc(2*var(--cell) + var(--ecart) + 5mm);min-width:calc(2*var(--cell) + var(--ecart) + 5mm)}
.cellule{flex:0 0 var(--cell);display:inline-flex;justify-content:flex-end;align-items:flex-end}
.cellule + .cellule{margin-left:var(--ecart)}
.cellule .blanc{width:11.6mm}

/* En-tête de la première colonne */
.tete{flex:0 0 auto;display:flex;flex-direction:column;align-items:center;text-align:center;padding:7mm 0 6.5mm}
.tete img{width:38mm;height:38mm;object-fit:contain;margin-bottom:2.5mm}
.tete-kicker{font-family:'KF Marque',sans-serif;font-weight:800;color:var(--jaune);text-transform:uppercase;letter-spacing:.14em;font-size:19pt;line-height:1}
.tete-nom{font-family:'KF Marque',sans-serif;font-weight:800;text-transform:uppercase;letter-spacing:.05em;font-size:30pt;line-height:1.08}
.tete-devise{font-size:12pt;font-weight:700;margin-top:1.2mm}

/* Décors élastiques : disque illustré + traits manuscrits */
.deco{flex:1 1 0;min-height:28mm;display:flex;align-items:center;justify-content:center;padding:3mm 0}
.scene{position:relative;height:100%;max-height:66mm;aspect-ratio:1.5;isolation:isolate}
.disque{position:absolute;top:0;bottom:0;left:50%;aspect-ratio:1;transform:translateX(-50%);border-radius:50%;background:#FFF4C7;
  border:.7mm solid var(--marine);display:grid;place-items:center}
.disque::before{content:"";position:absolute;inset:1.9mm;border-radius:50%;border:.4mm dashed var(--marine)}
.disque::after{content:"";position:absolute;inset:-.7mm;border-radius:50%;border:.6mm solid var(--jaune);transform:translate(2.4mm,2.2mm);z-index:-1}
.disque svg{width:64%;height:64%}
.fleche{position:absolute;width:26%;z-index:-1}
.zig{position:absolute;height:44%}
.arcs{position:absolute;height:74%;z-index:-2}
.pois{position:absolute;width:24%;aspect-ratio:1;border-radius:50%;background-image:radial-gradient(var(--noir) 26%,transparent 30%);background-size:22% 22%;z-index:-1}
.trois{position:absolute;display:flex;gap:1.6mm}
.trois i{width:2.6mm;height:2.6mm;border-radius:50%;background:var(--jaune)}
.deco-a .fleche{right:1%;top:2%;transform:rotate(18deg)} .deco-a .pois{left:3%;bottom:4%;transform:rotate(18deg)} .deco-a .zig{left:9%;top:2%} .deco-a .arcs{right:6%;bottom:-8%} .deco-a .trois{left:20%;bottom:0}
.deco-b .fleche{left:0;bottom:4%;transform:scaleX(-1) rotate(160deg)} .deco-b .pois{right:2%;top:6%;transform:rotate(-14deg)} .deco-b .zig{right:8%;bottom:2%} .deco-b .arcs{left:5%;top:-8%} .deco-b .trois{right:18%;bottom:1%}
.deco-c .fleche{left:1%;top:3%;transform:scaleX(-1) rotate(14deg)} .deco-c .pois{right:3%;bottom:5%;transform:rotate(30deg)} .deco-c .zig{right:9%;top:3%} .deco-c .arcs{left:6%;bottom:-8%} .deco-c .trois{right:20%;top:0}
"""

SCRIPT = """
/* Une fois les polices chargées : repère les « suites » passées à la ligne (pour les mettre en retrait)
   et réduit les titres trop longs pour leur bandeau. Pose data-pret="1" quand la page est prête. */
document.fonts.ready.then(() => {
  for (const ligne of document.querySelectorAll('.ligne')) {
    const nom = ligne.querySelector('.nom'), suite = ligne.querySelector('.suite');
    if (nom && suite && suite.getBoundingClientRect().top > nom.getBoundingClientRect().top + 4) suite.classList.add('a-la-ligne');
  }
  for (const titre of document.querySelectorAll('.titre')) {
    const texte = titre.firstElementChild, place = titre.clientWidth * 0.93;
    let taille = parseFloat(getComputedStyle(titre).fontSize);
    while (texte.getBoundingClientRect().width > place && taille > 20) { taille -= 0.5; titre.style.fontSize = taille + 'px'; }
  }
  document.body.dataset.pret = '1';
});
"""


def tranche(bloc_plan, rubrique):
    debut = bloc_plan[2] if len(bloc_plan) > 2 else 0
    fin = bloc_plan[3] if len(bloc_plan) > 3 and bloc_plan[3] is not None else len(rubrique["plats"])
    return debut, fin


def verifier_plan(plan, rubriques):
    """Chaque plat de chaque rubrique doit être placé une fois et une seule."""
    places = {t: [] for t in rubriques}
    for col in plan:
        for b in col:
            if b[0] == "section":
                if b[1] not in rubriques:
                    raise SystemExit(f"PLAN : rubrique inconnue → {b[1]}")
                places[b[1]].extend(range(*tranche(b, rubriques[b[1]])))
    for t, r in rubriques.items():
        if places[t] != list(range(len(r["plats"]))):
            raise SystemExit(f"PLAN : « {t} » mal placée ({len(places[t])} plats placés sur {len(r['plats'])}, ou dans le désordre)")
    # Les numéros doivent se suivre dans l'ordre de lecture : colonne après colonne, de haut en bas.
    lus = [rubriques[b[1]]["plats"][i]["num"] for col in plan for b in col if b[0] == "section"
           for i in range(*tranche(b, rubriques[b[1]]))]
    if lus != sorted(lus):
        k = next(i for i in range(1, len(lus)) if lus[i] < lus[i - 1])
        raise SystemExit(f"PLAN : la numérotation recule (n° {lus[k - 1]} puis n° {lus[k]}) — remettre nouveau-menu.txt dans l'ordre du PLAN")


def composer(avec_questions=True, mesure=False):
    liste = lire(SOURCE)
    rubriques = {r["titre"]: r for r in liste}
    plan = [[("section", t)] for t in rubriques] if mesure else PLAN
    plan = plan + [[] for _ in range(-len(plan) % 4)]            # pages complètes de 4 colonnes
    verifier_plan(plan, rubriques)
    nb_menu = len(plan) // 4
    pages_q = [] if mesure or not avec_questions else questions.pages(liste, TETE, rendu_deco)
    total = nb_menu + len(pages_q)

    def enveloppe(colonnes, numero, classe=""):
        return (f'<div class="page{classe}"><div class="filet-jaune"></div><div class="cadre">{colonnes}</div>'
                f'<div class="mention">{html.escape(MENTION)}</div><div class="folio">Page {numero} / {total}</div></div>')

    pages = []
    for p in range(nb_menu):
        cols = []
        for col in plan[4 * p:4 * p + 4]:
            blocs = []
            for b in col:
                if b[0] == "tete":
                    blocs.append(TETE)
                elif b[0] == "deco":
                    blocs.append(rendu_deco(b[1], b[2]))
                else:
                    r = rubriques[b[1]]
                    blocs.append(rendu_section(r, *tranche(b, r)))
            cols.append(f'<div class="col">{"".join(blocs)}</div>')
        pages.append(enveloppe("".join(cols), p + 1))
    for i, colonnes in enumerate(pages_q):
        pages.append(enveloppe(colonnes, nb_menu + i + 1, " page-notes"))
    doc = ('<!DOCTYPE html>\n<html lang="fr">\n<head>\n<meta charset="UTF-8">\n<title>KING FOOD — nouveau menu (prix à compléter)</title>\n'
           '<link rel="stylesheet" href="polices-menu.css">\n<style>' + CSS + questions.CSS + '</style>\n</head>\n<body>\n'
           + "\n".join(pages) + '\n<script>' + SCRIPT + '</script>\n</body>\n</html>\n')
    SORTIE.write_text(doc, encoding="utf-8")
    nb = sum(len(r["plats"]) for r in liste)
    print(f"{SORTIE.name} : {len(liste)} rubriques, {nb} plats, {nb_menu} pages de menu + {len(pages_q)} de questions")


if __name__ == "__main__":
    composer(avec_questions="--sans-questions" not in sys.argv[1:], mesure="--mesure" in sys.argv[1:])
