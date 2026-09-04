#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère le code QR permanent de la carte KING FOOD.

    python3 generer-qr.py                       → adresse définitive (ci-dessous)
    python3 generer-qr.py https://autre.adresse/ → une autre adresse (test, domaine futur…)

Dépendances : pip install segno pillow zxing-cpp

Fichiers produits dans ce dossier :
    qr-carte.svg           QR vectoriel, logo au centre s'il est présent — pour l'imprimeur
    qr-carte.png           le même en 2 000 px — WhatsApp, réseaux sociaux, Word…
    qr-carte-simple.svg    QR sans logo, lisibilité maximale
    qr-carte-simple.png

Le logo est lu dans le dossier parent : logo.svg (vectoriel, préféré) ou logo.png
(fond transparent). Sans logo, qr-carte.* est identique à qr-carte-simple.*.

Chaque PNG est ensuite relu par un décodeur pour prouver qu'il renvoie bien l'adresse,
y compris réduit à la taille d'un petit autocollant.
"""
import base64
import io
import re
import sys
import pathlib

import segno
import zxingcpp
from PIL import Image, ImageDraw

ICI = pathlib.Path(__file__).resolve().parent
ADRESSE = sys.argv[1] if len(sys.argv) > 1 else "https://hospiceantonio.github.io/kingfood/"

SOMBRE = "#111111"      # couleur des modules : garder une teinte foncée (charte : --kf-primaire-fonce)
BORD = 4                # marge blanche autour du code, en modules (norme ISO : 4)
MEDAILLON = 0.30        # diamètre du disque blanc du logo, en fraction du code
LOGO_DANS_DISQUE = 0.78 # taille du logo dans le disque


# ---------------------------------------------------------------- logo (optionnel)
LOGO_SVG = ICI.parent / "logo.svg"
LOGO_PNG = ICI / "logo-hd.png" if (ICI / "logo-hd.png").exists() else RACINE / "logo.png"   # haute définition si présente


def logo_disponible():
    return LOGO_SVG.exists() or LOGO_PNG.exists()


def logo_svg_inline(cote):
    """Balise SVG à placer dans le code : le logo.svg tel quel, sinon le logo.png embarqué."""
    if LOGO_SVG.exists():
        src = LOGO_SVG.read_text(encoding="utf-8")
        src = re.sub(r"<\?xml[^>]*>|<!DOCTYPE[^>]*>", "", src).strip()
        return re.sub(r"<svg", f'<svg width="{cote:.4f}" height="{cote:.4f}" preserveAspectRatio="xMidYMid meet"', src, count=1)
    donnees = base64.b64encode(LOGO_PNG.read_bytes()).decode()
    return (f'<image width="{cote:.4f}" height="{cote:.4f}" preserveAspectRatio="xMidYMid meet" '
            f'href="data:image/png;base64,{donnees}"/>')


# ---------------------------------------------------------------- SVG
def svg_qr(matrice, avec_logo):
    n = len(matrice)
    taille = n + 2 * BORD
    cx = cy = taille / 2
    rayon = MEDAILLON * n / 2 if avec_logo else 0

    traces = []
    for y, ligne in enumerate(matrice):
        for x, sombre in enumerate(ligne):
            if not sombre:
                continue
            # On retire les modules cachés par le disque : le vecteur reste propre.
            if avec_logo and (x + BORD + 0.5 - cx) ** 2 + (y + BORD + 0.5 - cy) ** 2 <= (rayon + 0.4) ** 2:
                continue
            traces.append(f"M{x + BORD} {y + BORD}h1v1h-1z")

    logo = ""
    if avec_logo:
        cote = 2 * rayon * LOGO_DANS_DISQUE
        logo = (
            f'<circle cx="{cx}" cy="{cy}" r="{rayon:.3f}" fill="#fff"/>\n'
            f'<g shape-rendering="geometricPrecision" '
            f'transform="translate({cx - cote / 2:.4f} {cy - cote / 2:.4f})">\n'
            f"{logo_svg_inline(cote)}\n</g>"
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {taille} {taille}" '
        f'width="{taille * 10}" height="{taille * 10}">\n'
        f"<title>Code QR — La carte KING FOOD</title>\n"
        f"<desc>{ADRESSE}</desc>\n"
        f'<rect width="{taille}" height="{taille}" fill="#fff"/>\n'
        f'<path d="{"".join(traces)}" fill="{SOMBRE}" shape-rendering="crispEdges"/>\n'
        f"{logo}\n</svg>\n"
    )


# ---------------------------------------------------------------- PNG
def png_qr(qr, n, avec_logo):
    echelle = max(1, round(2000 / (n + 2 * BORD)))
    tampon = io.BytesIO()
    qr.save(tampon, kind="png", scale=echelle, border=BORD, dark=SOMBRE, light="#ffffff")
    image = Image.open(tampon).convert("RGBA")

    if avec_logo:
        centre = image.width / 2
        rayon = MEDAILLON * n * echelle / 2
        ImageDraw.Draw(image).ellipse(
            [centre - rayon, centre - rayon, centre + rayon, centre + rayon], fill="white"
        )
        cote = int(2 * rayon * LOGO_DANS_DISQUE)
        if LOGO_PNG.exists():
            logo = Image.open(LOGO_PNG).convert("RGBA")
        else:
            # logo.svg seulement : on le rastérise via le SVG du code déjà produit ? Non — on
            # demande simplement un logo.png en plus pour la version PNG.
            sys.exit("Pour la version PNG avec logo, ajoutez aussi logo.png (export du logo.svg).")
        logo.thumbnail((cote, cote), Image.LANCZOS)
        image.alpha_composite(logo, (int(centre - logo.width / 2), int(centre - logo.height / 2)))

    return image.convert("RGB")


# ---------------------------------------------------------------- vérification
def verifier(chemin):
    image = Image.open(chemin)
    for cote in (image.width, 600, 300, 160):
        essai = image if cote == image.width else image.resize((cote, cote), Image.LANCZOS)
        lu = zxingcpp.read_barcodes(essai)
        ok = bool(lu) and lu[0].text == ADRESSE
        print(f"   {chemin.name:22s} relu à {cote:4d} px : {'OK' if ok else 'ÉCHEC'}")
        if not ok:
            sys.exit(f"Le fichier {chemin.name} ne se décode pas correctement — arrêt.")


# ---------------------------------------------------------------- principal
def main():
    # Correction d'erreur H (30 %) : le logo peut masquer le centre sans gêner la lecture.
    qr = segno.make(ADRESSE, error="h")
    matrice = [list(ligne) for ligne in qr.matrix]
    n = len(matrice)

    print(f"Adresse encodée : {ADRESSE}")
    print(f"Version {qr.version} — {n}×{n} modules — correction {qr.error} (30 %)")

    caches = 0 if not logo_disponible() else sum(
        1
        for y in range(n)
        for x in range(n)
        if (x + 0.5 - n / 2) ** 2 + (y + 0.5 - n / 2) ** 2 <= (MEDAILLON * n / 2 + 0.4) ** 2
    )
    print(f"Disque du logo : {caches} modules masqués sur {n * n} ({100 * caches / n / n:.1f} %)\n")

    if not logo_disponible():
        print("Aucun logo.svg / logo.png dans le dossier king-food/ : QR sans logo pour l'instant.\n")

    for nom, avec_logo in (("qr-carte", logo_disponible()), ("qr-carte-simple", False)):
        (ICI / f"{nom}.svg").write_text(svg_qr(matrice, avec_logo), encoding="utf-8")
        png_qr(qr, n, avec_logo).save(ICI / f"{nom}.png", optimize=True)
        print(f"→ {nom}.svg / {nom}.png")
        verifier(ICI / f"{nom}.png")

    print("\nTerminé. Le QR encode l'adresse ci-dessus ; changez la carte, jamais le QR.")


if __name__ == "__main__":
    main()
