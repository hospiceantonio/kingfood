#!/usr/bin/env python3
"""Ajoute au PDF un champ de saisie sur chaque case « prix » (positions relevées par rendre.js),
pour que les prix puissent être tapés directement dans le PDF. Imprimé, le PDF garde des cases vides
à remplir à la main.

    python3 outils/champs.py <entrée.pdf> <champs.json> <sortie.pdf>
"""
import json
import sys

import pymupdf

PX_EN_PT = 72 / 96   # les positions sont relevées en pixels CSS (96 par pouce)


def ajouter(entree, champs_json, sortie):
    doc = pymupdf.open(entree)
    champs = json.load(open(champs_json, encoding="utf-8"))
    for c in champs:
        page = doc[c["page"]]
        x0, y0 = c["x"] * PX_EN_PT, c["y"] * PX_EN_PT
        w = pymupdf.Widget()
        w.field_name = c["nom"]
        w.field_label = c["libelle"]                      # info-bulle : « Prix du n° 12 — Fattouche »
        w.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
        w.rect = pymupdf.Rect(x0, y0 - 1.5, x0 + c["l"] * PX_EN_PT, y0 + c["h"] * PX_EN_PT - 0.5)
        w.text_font, w.text_fontsize, w.text_color = "HeBo", 11.5, (0, 0, 0)
        w.fill_color, w.border_color, w.border_width = None, None, 0
        w.text_maxlen = 8
        w.field_value = ""
        page.add_widget(w)
        doc.xref_set_key(w.xref, "Q", "2")                # texte aligné à droite, contre le « F »
        w.update()
    doc.set_metadata({"title": "KING FOOD — nouveau menu (prix à compléter)", "author": "KING FOOD",
                      "subject": "Projet de nouveau menu : les prix se saisissent dans les cases ou s'écrivent à la main."})
    doc.save(sortie, garbage=3, deflate=True)
    print(f"{sortie} : {len(doc)} pages, {len(champs)} champs de saisie")


if __name__ == "__main__":
    ajouter(*sys.argv[1:4])
