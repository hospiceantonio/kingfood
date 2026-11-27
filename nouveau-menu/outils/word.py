#!/usr/bin/env python3
"""Prépare le contenu de la version Word du document à remplir par le restaurant.

Le PDF à champs de saisie s'est révélé difficile à remplir : la version Word reprend le même
contenu (les 248 plats et les mêmes questions) dans des tableaux simples, où toute case jaune
est une case à remplir. Ce script écrit le contenu en JSON ; word.js en fait le fichier .docx.

    python3 outils/word.py word-modele.json
    node outils/word.js word-modele.json KING-FOOD-nouveau-menu-v2-a-completer.docx

Le menu vient de nouveau-menu.txt (même lecture et mêmes numéros que le PDF). Le texte des
questions reprend celui de questions.py, reformulé pour des cases à remplir ; les listes
(rubriques absentes, noms incertains…) sont celles de questions.py."""
import json
import pathlib
import sys

import composer
import questions

LOGO = composer.ICI.parent / "qr" / "logo-hd.png"
NBSP = "\u00a0"


# ------------------------------------------------------------------ éléments d'une question
def choix(*options):
    """Une liste de choix : une case jaune par option, où l'on met un X."""
    return {"type": "choix", "options": list(options)}


def texte(invite="Votre réponse"):
    """Une case jaune pour une réponse libre."""
    return {"type": "texte", "invite": invite}


def p(contenu):
    return {"type": "p", "texte": contenu}


def noms(lignes):
    """Tableau « nom lu / bien lu (X) / sinon, le bon nom »."""
    return {"type": "noms", "lignes": lignes}


def grille(lignes, colonnes):
    """Tableau à cases : une ligne par rubrique, une case jaune par colonne."""
    return {"type": "grille", "lignes": lignes, "colonnes": colonnes}


def question(numero, titre, intro, *elements):
    return {"numero": str(numero), "titre": titre, "intro": intro, "elements": list(elements)}


# ------------------------------------------------------------------ contenu
def modele():
    rubriques = composer.lire(composer.SOURCE)
    plats = [pl for r in rubriques for pl in r["plats"]]
    nb = len(plats)
    par_titre = {r["titre"]: r for r in rubriques}
    numeros = {(r["titre"], pl["nom"]): pl["num"] for r in rubriques for pl in r["plats"]}

    def num(rubrique, nom):
        if (rubrique, nom) not in numeros:
            raise SystemExit(f"word.py : plat introuvable dans nouveau-menu.txt → {rubrique} / {nom}")
        return numeros[(rubrique, nom)]

    def no(rubrique, nom):
        return f"n°{NBSP}{num(rubrique, nom)}"

    def liste(nombres):
        nombres = [str(n) for n in nombres]
        return ", ".join(nombres[:-1]) + f" et {nombres[-1]}"

    coupes = [num("Burgers", nom) for nom in questions.BURGERS_COUPES]
    cuisine = [pl for t in questions.RUBRIQUES_CUISINE for pl in par_titre[t]["plats"]]
    sans_desc = sum(1 for pl in cuisine if not pl["desc"])
    viandes_rouges = par_titre["Viandes rouges"]["plats"][0]
    crevettes = "Crevettes sautées à l'ail"
    pizzas_incertaines = sorted(questions.NOMS_PIZZAS, key=lambda n: num("Pizzas", n[1]))

    groupes = [
        {"titre": "Vos feuilles du 24 novembre", "questions": [
            question(1, "Trois noms difficiles à lire",
                     "Avons-nous bien lu ? Mettez un X si le nom est bon, sinon écrivez le bon nom.",
                     noms([{"nom": f'{no("Nos pâtes", "Farfalle King Food")} — Farfalle King Food', "note": "(écrit « Fafal »)"},
                           {"nom": f'{no("Petit déjeuner oriental", "Sandwich malaké végétarien")} — Sandwich malaké végétarien', "note": ""},
                           {"nom": f'{no("Sandwichs", "Panini Vénito")} — Panini Vénito', "note": ""}])),
            question(2, f'Poulet strogonof ({no("Nouveautés du chef", "Poulet strogonof")})',
                     "Votre feuille lui donne la description « filet de bœuf, sauce aux poivres verts », la même que le steak "
                     f'{no("Nouveautés du chef", "Steak aux poivres verts")}. Quelle est la bonne description ?',
                     texte("La bonne description du poulet strogonof")),
            question(3, "Viandes rouges",
                     f'La rubrique commence en haut d\'une feuille, sans titre, par « {viandes_rouges["nom"]} » '
                     f'(n°{NBSP}{viandes_rouges["num"]}). Manque-t-il une feuille avant ?',
                     choix("Non, la liste est complète", "Oui, nous vous l'envoyons")),
            question(4, "Plats en double",
                     f'« {crevettes} » figure aux {no("Entrées chaudes", crevettes)} et {num("Brochettes & grillades", crevettes)} ; '
                     f'« Rouleaux aux fromages » aux {no("Petit déjeuner oriental", "Rouleau aux fromages")} et '
                     f'{num("Entrées chaudes", "Rouleaux aux fromages")}.',
                     choix("Garder les deux fois", "Garder une seule fois"),
                     texte("Si une seule fois : dans quelle rubrique les garder ?")),
        ]},
        {"titre": "Vos captures d'écran : chawarmas et burgers", "questions": [
            question(5, "Capture des burgers coupée",
                     f"La capture est coupée à droite : la composition des burgers n°{NBSP}{liste(coupes)} est illisible. "
                     "Elle porte aussi la mention « 3 sur 4 » : nous n'avons reçu que deux pages sur quatre.",
                     choix("Nous renvoyons les quatre pages", "Laisser ces burgers sans composition"),
                     texte("Ou écrivez ici les compositions manquantes")),
            question(6, f'Burger végétarien ({no("Burgers", "Burger végétarien")})',
                     "Deux compositions. Feuille du 24 novembre : « aubergine, tomate, oignon, frites, cornichon ». "
                     "Capture : « laitue, tomate, choux, frites, sauce cocktail, champignon, oignon », retenue ici. Laquelle garder ?",
                     choix("Celle de la capture", "Celle de la feuille")),
            question(7, f'Zinger burger ({no("Burgers", "Zinger burger")})',
                     "Il figure sur votre feuille du 24 novembre, pas sur la capture. Faut-il le garder ?",
                     choix("Le garder", "Le retirer"),
                     texte("Sa composition")),
        ]},
        {"titre": "Pizzas", "questions": [
            question(8, "Deux tailles",
                     "L'ancien menu donnait deux prix par pizza, petite et grande. Nous avons prévu deux cases par pizza.",
                     choix("Oui, petite et grande", "Non, une seule taille")),
            question(9, "Six noms à confirmer",
                     "Mettez un X si le nom est bien lu, sinon écrivez le bon nom.",
                     noms([{"nom": f'{no("Pizzas", n[1])} — {n[1]}', "note": n[2] if len(n) > 2 else ""} for n in pizzas_incertaines])),
            question(10, "Deux compositions à vérifier",
                     f'**Fruits de mer** ({no("Pizzas", "Fruits de mer")}) : aucun fromage n\'est écrit, alors que les autres pizzas ont de la mozzarella.',
                     choix("Ajouter « mozzarella »", "Sans fromage"),
                     p(f'**Country** ({no("Pizzas", "Country")}) : nous lisons « émincé de poulet saucisse ». Poulet et saucisse ?'),
                     choix("Oui, poulet et saucisse"),
                     texte("Sinon, la bonne composition")),
            question(11, "Deux noms presque identiques",
                     f'« Chef » ({no("Pizzas", "Chef")}, au poulet) et « Suggestion du chef » ({no("Pizzas", "Suggestion du chef")}, au bœuf) '
                     "risquent d'être confondues à la commande.",
                     choix("Garder les deux noms", "Renommer une des deux"),
                     texte("Le nouveau nom")),
            question(12, "Pizzas de l'ancien menu",
                     f"Cinq pizzas de l'ancien menu ne sont plus sur vos feuilles : {questions.PIZZAS_DISPARUES}.",
                     choix("Elles sont supprimées", "Les garder")),
        ]},
        {"titre": "Boissons", "questions": [
            question(13, "Cocktails de l'ancien menu",
                     f"Six cocktails ne sont plus sur vos feuilles : {questions.COCKTAILS_DISPARUS}.",
                     choix("Ils sont supprimés", "Les garder")),
            question(14, "Boissons : trois noms",
                     f'Vos feuilles disent « Extra » ({no("Boissons", "Extra")}) et « Énergie » ({no("Boissons", "Énergie")}) ; '
                     "l'ancien menu disait « Jus Extra » et « Flash Énergie ». Quels noms imprimer ?",
                     texte("Les noms à imprimer"),
                     p("« Frisco » n'est plus sur la liste :"),
                     choix("Supprimé", "À garder")),
        ]},
        {"titre": "Ancien menu", "questions": [
            question(15, "Prix des desserts et des boissons",
                     "Crêpes, gaufres, gâteaux, glaces, jus, boissons chaudes et chicha sont les mêmes que sur l'ancien menu imprimé. "
                     "Faut-il reprendre ses prix ?",
                     choix("Oui, reprendre les anciens prix", "Non, nous écrivons les nouveaux prix dans le menu")),
            question(16, "Rubriques encore absentes",
                     "Aucune feuille ne parle de ces rubriques de l'ancien menu. Faut-il les garder comme avant, ou les supprimer ? "
                     "Mettez un X dans une case par ligne.",
                     grille(questions.RUBRIQUES_ABSENTES, ["Garder", "Supprimer"]),
                     p("Sur vos photos, on aperçoit d'autres feuilles sous les piles : « choukouya », « ailerons de dinde », « Africains », "
                       "des ventes au kilo. Font-elles partie du menu ?"),
                     choix("Oui, nous les envoyons", "Non")),
        ]},
    ]

    suggestions = [
        question("A", "Accompagnements",
                 "L'ancien menu les listait : riz, frites, aloco, attiéké, pâte… Nous suggérons de les rappeler, en disant s'ils sont "
                 "compris dans le prix.",
                 choix("Compris dans le prix", "En supplément"),
                 texte("Prix du supplément, en F"),
                 texte("Liste des accompagnements à jour")),
        question("B", "Descriptions",
                 f"{sans_desc} plats cuisinés n'ont pas de description, par exemple « Sandwich samaké » ou « Crevettes à l'indienne ». "
                 "Une ligne courte aide le client à choisir.",
                 choix("Laisser ainsi", "Nous les écrivons dans le menu, sous le nom du plat", "Nous vous les envoyons à part")),
        question("C", "Fruits et eaux",
                 "« Assiette de fruits », « Assiette de raisin » et « Eau gazeuse » sont rangées dans « Jus mixte », « Salade de fruits » "
                 "dans « Boissons ». Nous suggérons une rubrique « Fruits » avec les desserts, et les eaux avec les boissons.",
                 choix("Oui, les ranger ainsi", "Laisser comme sur la feuille")),
        question("D", "Photos des plats",
                 "Le menu final sera illustré par des dessins. Avec six à huit photos nettes de vos plats, nous pouvons mettre des photos, "
                 "comme sur l'ancien menu.",
                 choix("Garder les dessins", "Nous envoyons des photos")),
        question("E", "Menu en ligne (code QR)",
                 "Le code QR ouvre encore l'ancien menu. Une fois les prix validés, il peut afficher le nouveau : le code déjà imprimé "
                 "ne change pas.",
                 choix("Oui, le mettre à jour", "Pas pour l'instant")),
    ]

    return {
        "logo": str(LOGO),
        "mention": "KING FOOD · Nouveau menu, version 2 · Document à compléter · 27 novembre 2026",
        "etiquette": "Version 2 · à compléter et à renvoyer",
        "nb": nb,
        "mode_emploi": [
            "Ouvrez ce fichier avec **Word**, sur un ordinateur ou sur un téléphone.",
            "**Toutes les cases jaunes sont à remplir.** Touchez une case jaune, puis tapez.",
            f"**Le menu.** Tapez le prix de chacun des {nb} plats dans sa case jaune. Les burgers et les pizzas ont deux prix.",
            "**Les questions**, à la fin. Mettez un **X** dans la case jaune de votre choix, ou tapez votre réponse.",
            "Un nom ou une description à corriger ? Corrigez directement dans le tableau.",
            "**Enregistrez** le fichier et renvoyez-le par WhatsApp.",
        ],
        "encadres": [
            "**Vous préférez le papier ?** Imprimez ce document, écrivez à la main dans les cases jaunes, puis envoyez une photo nette "
            "de chaque page.",
            "**Vous avez déjà noté des prix ailleurs ?** Ne recopiez rien : envoyez-les tels quels, nous les reporterons. "
            "Attention, les numéros des plats ont changé depuis la première version.",
        ],
        "rubriques": [{"titre": r["titre"], "note": r["note"], "formats": r["formats"],
                       "plats": [{k: pl[k] for k in ("num", "nom", "desc", "formats", "prix")} for pl in r["plats"]]} for r in rubriques],
        "fait": [
            "L'orthographe est corrigée, sans changer les plats : champignon, maïs doux, émincé, Calzone, Margherita, Méditerranée, "
            "Toscane, Malgache…",
            "Chawarmas et burgers : noms et compositions sont repris de vos captures d'écran. Leurs prix sont laissés vides : "
            "vous inscrivez vos prix à jour.",
            "Pizzas : le mot « pizza » n'est plus répété devant chaque nom, et « fromage mozzarella » devient « mozzarella ».",
            "Pizza Chicken : « poivron », écrit deux fois, n'apparaît qu'une fois.",
            "Les lignes barrées ne sont pas reprises : « Coca-Cola bouteille en verre » (deux lignes) et « Lapin à la moutarde ».",
            "« Sandwich libanais » devient « Sandwichs » et « Suite viande rouge brochette » devient « Brochettes & grillades ».",
            f"Les rubriques sont rangées dans l'ordre d'un repas, et les plats numérotés de 1 à {nb}.",
            "Le menu final gardera la présentation de l'ancien menu imprimé. Ce document Word sert seulement à recueillir vos prix "
            "et vos réponses.",
        ],
        "fait_invite": "Un de ces choix ne vous convient pas ? Dites-le ici",
        "groupes": groupes,
        "suggestions": suggestions,
    }


if __name__ == "__main__":
    sortie = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "word-modele.json")
    m = modele()
    sortie.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    nq = sum(len(g["questions"]) for g in m["groupes"])
    print(f"{sortie.name} : {len(m['rubriques'])} rubriques, {m['nb']} plats, {nq} questions, {len(m['suggestions'])} suggestions")
