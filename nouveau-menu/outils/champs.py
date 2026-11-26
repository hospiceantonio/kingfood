#!/usr/bin/env python3
"""Ajoute au PDF un champ de saisie sur chaque case à remplir (positions relevées par rendre.js) :
les prix, les lignes de réponse et les cases à cocher de la page de questions. Le document se
remplit ainsi à l'écran ; imprimé, il garde des cases vides à remplir à la main.

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
        x1, y1 = x0 + c["l"] * PX_EN_PT, y0 + c["h"] * PX_EN_PT
        w = pymupdf.Widget()
        w.field_name = c["nom"]
        w.field_label = c["libelle"]                      # info-bulle : « Prix du n° 12 — Fattouche »
        w.fill_color, w.border_color, w.border_width = None, None, 0
        w.text_color = (0, 0, 0)
        if c["type"] == "case":                           # case à cocher, posée dans le carré imprimé
            w.field_type = pymupdf.PDF_WIDGET_TYPE_CHECKBOX
            w.rect = pymupdf.Rect(x0 + 0.8, y0 + 0.8, x1 - 0.8, y1 - 0.8)
            w.field_value = False
        elif c["type"] == "texte":                        # réponse libre, sur une ou plusieurs lignes
            w.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
            w.rect = pymupdf.Rect(x0, y0 + 1, x1, y1 - 1)
            w.text_font, w.text_fontsize = "Helv", 11
            if c["h"] > 40:                               # plus d'une ligne imprimée
                w.field_flags = pymupdf.PDF_TX_FIELD_IS_MULTILINE
            w.field_value = ""
        else:                                             # prix : court, aligné à droite contre le « F »
            w.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
            w.rect = pymupdf.Rect(x0, y0 - 1.5, x1, y1 - 0.5)
            # case étroite (rubrique à deux colonnes de prix) : corps réduit pour qu'un prix à cinq chiffres tienne
            w.text_font, w.text_fontsize = "HeBo", 11.5 if x1 - x0 >= 36 else 10.5
            w.text_maxlen = 8
            w.field_value = ""
        page.add_widget(w)
        if c["type"] == "prix":
            doc.xref_set_key(w.xref, "Q", "2")
            w.update()
    doc.set_metadata({"title": "KING FOOD — nouveau menu, version 2 (prix à compléter)", "author": "KING FOOD",
                      "subject": "Projet de nouveau menu : prix et réponses à saisir dans les cases, ou à écrire à la main."})
    doc.save(sortie, garbage=3, deflate=True)
    compte = {t: sum(1 for c in champs if c["type"] == t) for t in ("prix", "texte", "case")}
    print(f"{sortie} : {len(doc)} pages · {compte['prix']} prix, {compte['texte']} réponses, {compte['case']} cases à cocher")


if __name__ == "__main__":
    ajouter(*sys.argv[1:4])
