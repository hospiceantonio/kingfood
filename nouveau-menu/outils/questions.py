"""Pages « mode d'emploi, déjà fait, à confirmer, nos suggestions », ajoutées à la suite du menu
dans le PDF envoyé au restaurant.

Les numéros de plats cités sont retrouvés par (rubrique, nom) dans nouveau-menu.txt : ils restent
justes si la numérotation change. Chaque case à cocher et chaque ligne de réponse porte un attribut
data-champ : rendre.js relève sa position et champs.py en fait un champ de saisie du PDF.

`pages()` renvoie, pour chaque page, le HTML de ses quatre colonnes ; composer.py y ajoute le cadre."""
import html

e = html.escape

# Rubriques de l'ancien menu imprimé dont aucune feuille reçue ne parle
RUBRIQUES_ABSENTES = [
    "Grillades : choukouya, ailerons de dinde, mouton braisé",
    "Sauces gluantes et liquides",
    "Plats africains : kédjénou, tchiep, n'dolé…",
    "Suggestions du chef : ragoût d'igname…",
    "Accompagnements",
]
# Plats de l'ancien menu imprimé absents des nouvelles listes (comparaison avec menu.json en ligne)
PIZZAS_DISPARUES = "Pêcheur, Italienne, 4 Saisons, Love, Surprise"
COCKTAILS_DISPARUS = "Pink Banana, Milky Mango, Green or Red Moon, Papaye ou t'es, Kid dit wi, Mangua Gogo"
# Noms de pizzas dont la lecture est incertaine : (clé du champ, nom retenu, ce qui est écrit)
NOMS_PIZZAS = [("crazy", "Crazy Bun's"), ("capri", "Capri", "(écrit «\u00a0Capi\u00a0»)"), ("thonata", "Thonata", "(«\u00a0Thanata\u00a0»)"),
               ("miami", "Miami", "(«\u00a0Miani\u00a0»)"), ("triskell", "Triskell"), ("dg", "DG")]
# Rubriques de plats cuisinés : c'est là qu'une description manquante gêne le client
RUBRIQUES_CUISINE = ["Petit déjeuner", "Petit déjeuner oriental", "Nos entrées froides", "Entrées chaudes", "Sandwichs", "Burgers",
                     "Nos pâtes", "Fruits de mer", "Menu enfants", "Viandes rouges", "Brochettes & grillades", "Viandes blanches",
                     "Nouveautés du chef"]


# ------------------------------------------------------------------ briques
def coche(nom, libelle):
    return f'<span class="coche" data-champ="{nom}" data-type="case" data-libelle="{e(libelle, quote=True)}"></span>'


def choix(prefixe, question, *options):
    """Une rangée de cases à cocher : choix('q3', 'Feuille manquante', ('non', 'Non…'), ('oui', 'Oui…'))."""
    return '<div class="choix">' + "".join(
        f'<span class="option">{coche(f"{prefixe}_{cle}", f"{question} : {texte}")}{e(texte)}</span>' for cle, texte in options) + '</div>'


def reponse(nom, libelle, lignes=2):
    return (f'<div class="reponse" data-champ="{nom}" data-type="texte" data-libelle="{e(libelle, quote=True)}">'
            + '<i></i>' * lignes + '</div>')


def ligne(nom, libelle):
    return f'<span class="champ-ligne" data-champ="{nom}" data-type="texte" data-libelle="{e(libelle, quote=True)}"></span>'


def bloc(numero, titre, corps):
    return (f'<div class="q"><div class="q-tete"><span class="q-num">{numero}</span>'
            f'<span class="q-titre">{e(titre)}</span></div>{corps}</div>')


def titre(texte):
    return f'<h2 class="titre"><span>{e(texte)}</span></h2>'


def sous_titre(texte):
    return f'<p class="sous-titre">{e(texte)}</p>'


def colonnes(*cols):
    return "".join(f'<div class="col">{c}</div>' for c in cols)


# ------------------------------------------------------------------ contenu
def pages(rubriques, tete, deco):
    plats = [p for r in rubriques for p in r["plats"]]
    nb = len(plats)
    par_titre = {r["titre"]: r for r in rubriques}
    numeros = {(r["titre"], p["nom"]): p["num"] for r in rubriques for p in r["plats"]}

    def num(rubrique, nom):
        if (rubrique, nom) not in numeros:
            raise SystemExit(f"questions.py : plat introuvable dans nouveau-menu.txt → {rubrique} / {nom}")
        return numeros[(rubrique, nom)]

    def no(rubrique, nom):
        return f'n°&nbsp;{num(rubrique, nom)}'

    def nom_lu(cle, rubrique, nom, note=""):
        return (f'<div class="nom-lu">{no(rubrique, nom)} — {e(nom)}{f" <em>{e(note)}</em>" if note else ""}</div>'
                f'<div class="choix"><span class="option">{coche(f"{cle}_ok", f"{nom} : bien lu")}Bien lu</span>'
                f'<span class="option large">Sinon&nbsp;:{ligne(f"{cle}_nom", f"Bon nom à la place de {nom}")}</span></div>')

    deux_cases = [p for p in plats if p["formats"]]
    avec_prix = sum(1 for p in plats if p["prix"])
    burgers = par_titre["Burgers"]["plats"]
    coupes = [p for p in burgers if not p["prix"] and p["nom"] != "Zinger burger"]
    cuisine = [p for t in RUBRIQUES_CUISINE for p in par_titre[t]["plats"]]
    sans_desc = sum(1 for p in cuisine if not p["desc"])
    viandes_rouges = par_titre["Viandes rouges"]["plats"][0]
    crevettes = "Crevettes sautées à l'ail"

    # ================================================================ page 1 des questions
    liste_deux = ", ".join(str(p["num"]) for p in deux_cases[:-1]) + f' et {deux_cases[-1]["num"]}'
    col_mode = tete + '<div class="etiquette">Version 2 · à compléter et à renvoyer</div>' + titre("Mode d'emploi") + f'''
<p class="note">Voici la version 2 du projet&nbsp;: vos nouvelles feuilles et vos captures d'écran y sont ajoutées. Le menu compte
maintenant {nb} plats, numérotés de 1 à {nb}, pages 1 à 4.</p>
<ol class="etapes">
  <li><b>Les prix.</b> Écrivez le prix de chaque plat dans la case placée avant le «&nbsp;F&nbsp;»&nbsp;: à l'écran en cliquant dans la case, ou à la main.</li>
  <li><b>Prix déjà inscrits.</b> {avec_prix} plats (chawarmas et burgers) portent les prix de vos captures&nbsp;: vérifiez-les.</li>
  <li><b>Deux prix.</b> Burgers&nbsp;: sandwich et assiette. Pizzas&nbsp;: petite et grande. N°&nbsp;{liste_deux}&nbsp;: deux cases sous le nom.</li>
  <li><b>Les questions.</b> Répondez aux points des pages 5 et 6&nbsp;: une case à cocher ou quelques mots suffisent.</li>
  <li><b>Le retour.</b> Renvoyez ce document rempli, ou une photo nette de chaque page.</li>
</ol>
<div class="encadre"><b>Vous avez déjà noté des prix sur la version 1&nbsp;?</b> Ne recopiez rien&nbsp;: renvoyez-la aussi, nous reporterons vos prix.
Attention, les numéros des plats ont changé.</div>'''

    col_fait = titre("Déjà fait") + f'''
<ul class="fait">
  <li>L'orthographe est corrigée, sans changer les plats&nbsp;: champignon, maïs doux, émincé, Calzone, Margherita, Méditerranée, Toscane, Malgache…</li>
  <li>Chawarmas et burgers&nbsp;: noms, compositions et prix sont repris de vos captures d'écran.</li>
  <li>Pizzas&nbsp;: le mot «&nbsp;pizza&nbsp;» n'est plus répété devant chaque nom, et «&nbsp;fromage mozzarella&nbsp;» devient «&nbsp;mozzarella&nbsp;».</li>
  <li>Pizza Chicken&nbsp;: «&nbsp;poivron&nbsp;», écrit deux fois, n'apparaît qu'une fois.</li>
  <li>Les lignes barrées ne sont pas reprises&nbsp;: «&nbsp;Coca-Cola bouteille en verre&nbsp;» (deux lignes) et «&nbsp;Lapin à la moutarde&nbsp;».</li>
  <li>«&nbsp;Sandwich libanais&nbsp;» devient «&nbsp;Sandwichs&nbsp;» et «&nbsp;Suite viande rouge brochette&nbsp;» devient «&nbsp;Brochettes &amp; grillades&nbsp;».</li>
  <li>Les rubriques sont rangées dans l'ordre d'un repas, et les plats numérotés de 1 à {nb}.</li>
  <li>Des dessins remplacent pour l'instant les photos de l'ancien menu.</li>
</ul>
<p class="note">Un de ces choix ne vous convient pas&nbsp;? Dites-le ici&nbsp;:</p>''' + reponse("fait_remarques", "Remarques sur ce qui a déjà été fait", 3)

    q1 = bloc(1, "Trois noms difficiles à lire",
              '<p>Avons-nous bien lu&nbsp;? Cochez, ou écrivez le bon nom.</p>'
              + nom_lu("q1_farfalle", "Nos pâtes", "Farfalle King Food", "(écrit «\u00a0Fafal\u00a0»)")
              + nom_lu("q1_malake", "Petit déjeuner oriental", "Sandwich malaké végétarien")
              + nom_lu("q1_venito", "Sandwichs", "Panini Vénito"))
    q2 = bloc(2, f'Poulet strogonof (n°\u00a0{num("Nouveautés du chef", "Poulet strogonof")})',
              '<p>Votre feuille lui donne la description «&nbsp;filet de bœuf, sauce aux poivres verts&nbsp;», la même que le steak '
              + no("Nouveautés du chef", "Steak aux poivres verts") + '. Quelle est la bonne&nbsp;?</p>'
              + reponse("q2_description", "Bonne description du poulet strogonof", 2))
    q3 = bloc(3, "Viandes rouges",
              f'<p>La rubrique commence en haut d\'une feuille, sans titre, par «&nbsp;{e(viandes_rouges["nom"])}&nbsp;» '
              f'(n°&nbsp;{viandes_rouges["num"]}). Manque-t-il une feuille avant&nbsp;?</p>'
              + choix("q3", "Feuille manquante avant les viandes rouges", ("non", "Non, la liste est complète"), ("oui", "Oui, nous vous l'envoyons")))
    q4 = bloc(4, "Plats en double",
              '<p>«&nbsp;Crevettes sautées à l\'ail&nbsp;» figure aux ' + no("Entrées chaudes", crevettes)
              + f' et {num("Brochettes & grillades", crevettes)}&nbsp;; «&nbsp;Rouleaux aux fromages&nbsp;» aux '
              + no("Petit déjeuner oriental", "Rouleau aux fromages") + f' et {num("Entrées chaudes", "Rouleaux aux fromages")}.</p>'
              + choix("q4", "Plats en double", ("deux", "Garder les deux fois"), ("un", "Garder une seule fois"))
              + '<p class="serre">Dans quelle rubrique les garder&nbsp;?</p>' + reponse("q4_rubrique", "Rubrique où garder les plats en double", 1))
    col_24 = titre("À confirmer") + sous_titre("Vos feuilles du 24 novembre") + q1 + q2 + q3 + q4

    q5 = bloc(5, "Prix des chawarmas et des burgers",
              '<p>Les prix inscrits viennent de vos captures. Presque tous sont plus bas que sur l\'ancien menu imprimé&nbsp;: '
              'chawarma végétarien 1500&nbsp;F contre 2000&nbsp;F, hamburger viande 3000&nbsp;F contre 3500&nbsp;F. Lesquels sont les bons&nbsp;?</p>'
              + choix("q5", "Prix des chawarmas et burgers", ("captures", "Ceux des captures"), ("corriges", "Nous les corrigeons sur le menu")))
    q6 = bloc(6, "Capture des burgers coupée",
              f'<p>La capture est coupée à droite&nbsp;: les prix des n°&nbsp;{coupes[0]["num"]} à {coupes[-1]["num"]} et la fin de leur composition '
              'sont illisibles. Elle porte aussi la mention «&nbsp;3 sur 4&nbsp;»&nbsp;: nous n\'avons reçu que deux pages sur quatre.</p>'
              + choix("q6", "Capture des burgers", ("pages", "Nous renvoyons les quatre pages"), ("menu", "Nous écrivons les prix sur le menu")))
    q7 = bloc(7, f'Burger végétarien (n°\u00a0{num("Burgers", "Burger végétarien")})',
              '<p>Deux compositions. Feuille du 24 novembre&nbsp;: «&nbsp;aubergine, tomate, oignon, frites, cornichon&nbsp;». '
              'Capture&nbsp;: «&nbsp;laitue, tomate, choux, frites, sauce cocktail, champignon, oignon&nbsp;», retenue ici.</p>'
              + choix("q7", "Composition du burger végétarien", ("capture", "Celle de la capture"), ("feuille", "Celle de la feuille")))
    q8 = bloc(8, f'Zinger burger (n°\u00a0{num("Burgers", "Zinger burger")})',
              '<p>Il figure sur votre feuille du 24 novembre, pas sur la capture. Faut-il le garder&nbsp;?</p>'
              + choix("q8", "Zinger burger", ("garder", "Le garder"), ("retirer", "Le retirer"))
              + '<p class="serre">Sa composition&nbsp;:</p>' + reponse("q8_composition", "Composition du Zinger burger", 1))
    col_captures = titre("À confirmer (suite)") + sous_titre("Vos captures : chawarmas et burgers") + q5 + q6 + q7 + q8

    page_a = colonnes(col_mode, col_fait + deco("toque", "c"), col_24 + deco("salade", "b"), col_captures + deco("burger", "a"))

    # ================================================================ page 2 des questions
    def rang_nom(cle, nom, note=""):
        return (f'<span class="rang-nom">{num("Pizzas", nom)} — {e(nom)}{f" <em>{e(note)}</em>" if note else ""}</span>'
                + coche(f"q10_{cle}_ok", f"Pizza {nom} : bien lu") + ligne(f"q10_{cle}_nom", f"Bon nom à la place de {nom}"))

    q9 = bloc(9, "Deux tailles",
              '<p>L\'ancien menu donnait deux prix par pizza, petite et grande. Nous avons prévu deux cases par pizza.</p>'
              + choix("q9", "Tailles des pizzas", ("deux", "Oui, petite et grande"), ("une", "Non, une seule taille")))
    q10 = bloc(10, "Six noms à confirmer",
               '<p>Cochez si le nom est bien lu, sinon écrivez le bon.</p>'
               '<div class="grille-noms"><span></span><span class="tete-col">Bien lu</span><span class="tete-col gauche">Sinon</span>'
               + "".join(rang_nom(*n) for n in sorted(NOMS_PIZZAS, key=lambda n: num("Pizzas", n[1]))) + '</div>')
    q11 = bloc(11, "Deux compositions à vérifier",
               '<p><b>Fruits de mer</b> (' + no("Pizzas", "Fruits de mer") + ')&nbsp;: aucun fromage n\'est écrit, alors que les autres pizzas ont de la mozzarella.</p>'
               + choix("q11_fromage", "Pizza Fruits de mer", ("ajouter", "Ajouter « mozzarella »"), ("sans", "Sans fromage"))
               + '<p class="serre"><b>Country</b> (' + no("Pizzas", "Country") + ')&nbsp;: nous lisons «&nbsp;émincé de poulet saucisse&nbsp;». Poulet et saucisse&nbsp;?</p>'
               + '<div class="choix"><span class="option">' + coche("q11_country_oui", "Pizza Country : poulet et saucisse") + 'Oui</span>'
               + '<span class="option large">Non&nbsp;:' + ligne("q11_country_non", "Pizza Country : bonne composition") + '</span></div>')
    col_pizzas = titre("À confirmer : pizzas") + q9 + q10 + q11

    q12 = bloc(12, "Deux noms presque identiques",
               '<p>«&nbsp;Chef&nbsp;» (' + no("Pizzas", "Chef") + ', au poulet) et «&nbsp;Suggestion du chef&nbsp;» (' + no("Pizzas", "Suggestion du chef")
               + ', au bœuf) risquent d\'être confondues à la commande.</p>'
               + '<div class="choix"><span class="option">' + coche("q12_garder", "Pizzas Chef et Suggestion du chef : garder les deux noms") + 'Garder les deux noms</span></div>'
               + '<div class="choix"><span class="option large">' + coche("q12_renommer", "Renommer une des deux pizzas") + 'Renommer&nbsp;:'
               + ligne("q12_nom", "Nouveau nom d'une des deux pizzas") + '</span></div>')
    q13 = bloc(13, "Pizzas de l'ancien menu",
               f'<p>Cinq pizzas de l\'ancien menu ne sont plus sur vos feuilles&nbsp;: {e(PIZZAS_DISPARUES)}.</p>'
               + choix("q13", "Pizzas absentes des nouvelles feuilles", ("supprimees", "Elles sont supprimées"), ("garder", "Les garder")))
    q14 = bloc(14, "Cocktails de l'ancien menu",
               f'<p>Six cocktails ne sont plus sur vos feuilles&nbsp;: {e(COCKTAILS_DISPARUS)}.</p>'
               + choix("q14", "Cocktails absents des nouvelles feuilles", ("supprimes", "Ils sont supprimés"), ("garder", "Les garder")))
    q15 = bloc(15, "Boissons : trois noms",
               '<p>Vos feuilles disent «&nbsp;Extra&nbsp;» (' + no("Boissons", "Extra") + ') et «&nbsp;Énergie&nbsp;» (' + no("Boissons", "Énergie")
               + ')&nbsp;; l\'ancien menu disait «&nbsp;Jus Extra&nbsp;» et «&nbsp;Flash Énergie&nbsp;». Quels noms imprimer&nbsp;?</p>'
               + reponse("q15_noms", "Noms à imprimer pour Extra et Énergie", 1)
               + '<p class="serre">«&nbsp;Frisco&nbsp;» n\'est plus sur la liste&nbsp;:</p>'
               + choix("q15_frisco", "Frisco", ("supprime", "Supprimé"), ("garder", "À garder")))
    col_suite = titre("Pizzas, boissons") + q12 + q13 + q14 + q15

    grille = '<div class="grille"><span></span><span class="tete-col">Garder</span><span class="tete-col">Supprimer</span>' + "".join(
        f'<span>{e(r)}</span>' + coche(f"q17_{i + 1}_garder", f"{r} : garder") + coche(f"q17_{i + 1}_supprimer", f"{r} : supprimer")
        for i, r in enumerate(RUBRIQUES_ABSENTES)) + '</div>'
    q16 = bloc(16, "Prix des desserts et des boissons",
               '<p>Crêpes, gaufres, gâteaux, glaces, jus, boissons chaudes et chicha sont les mêmes que sur l\'ancien menu imprimé. '
               'Faut-il reprendre ses prix&nbsp;?</p>'
               + choix("q16", "Prix des desserts et boissons", ("anciens", "Oui, reprendre les anciens prix"), ("nouveaux", "Non, nous écrivons les nouveaux")))
    q17 = bloc(17, "Rubriques encore absentes",
               '<p>Aucune feuille ne parle de ces rubriques de l\'ancien menu. Faut-il les garder comme avant, ou les supprimer&nbsp;?</p>' + grille
               + '<p class="serre">Sur vos photos, on aperçoit d\'autres feuilles sous les piles&nbsp;: «&nbsp;choukouya&nbsp;», «&nbsp;ailerons de dinde&nbsp;», '
               '«&nbsp;Africains&nbsp;», des ventes au kilo. Font-elles partie du menu&nbsp;?</p>'
               + choix("q17_feuilles", "Feuilles aperçues sur les photos", ("envoi", "Oui, nous les envoyons"), ("non", "Non")))
    col_ancien = titre("Ancien menu") + q16 + q17

    sa = bloc("A", "Accompagnements",
              '<p>L\'ancien menu les listait&nbsp;: riz, frites, aloco, attiéké, pâte… Nous suggérons de les rappeler, en disant s\'ils sont compris dans le prix.</p>'
              + '<div class="choix"><span class="option">' + coche("sA_compris", "Accompagnements : compris dans le prix") + 'Compris</span>'
              + '<span class="option large">' + coche("sA_supplement", "Accompagnements : en supplément") + 'En supplément&nbsp;:'
              + ligne("sA_prix", "Prix de l'accompagnement en supplément") + 'F</span></div>'
              + '<p class="serre">Liste à jour&nbsp;:</p>' + reponse("sA_liste", "Liste des accompagnements", 1))
    sb = bloc("B", "Descriptions",
              f'<p>{sans_desc} plats cuisinés n\'ont pas de description, par exemple «&nbsp;Sandwich samaké&nbsp;» ou «&nbsp;Crevettes à l\'indienne&nbsp;». '
              'Une ligne courte aide le client à choisir.</p>'
              + choix("sB", "Descriptions manquantes", ("ainsi", "Laisser ainsi"), ("envoi", "Nous vous les envoyons")))
    sc = bloc("C", "Fruits et eaux",
              '<p>«&nbsp;Assiette de fruits&nbsp;», «&nbsp;Assiette de raisin&nbsp;» et «&nbsp;Eau gazeuse&nbsp;» sont rangées dans «&nbsp;Jus mixte&nbsp;», '
              '«&nbsp;Salade de fruits&nbsp;» dans «&nbsp;Boissons&nbsp;». Nous suggérons une rubrique «&nbsp;Fruits&nbsp;» avec les desserts, et les eaux avec les boissons.</p>'
              + choix("sC", "Ranger les fruits et les eaux", ("oui", "Oui, les ranger ainsi"), ("non", "Laisser comme sur la feuille")))
    sd = bloc("D", "Photos des plats",
              '<p>Avec six à huit photos nettes de vos plats, nous pouvons remplacer les dessins par des photos, comme sur l\'ancien menu.</p>'
              + choix("sD", "Photos des plats", ("dessins", "Garder les dessins"), ("photos", "Nous envoyons des photos")))
    se = bloc("E", "Menu en ligne (code QR)",
              '<p>Le code QR ouvre encore l\'ancien menu. Une fois les prix validés, il peut afficher le nouveau&nbsp;: le code déjà imprimé ne change pas.</p>'
              + choix("sE", "Menu en ligne", ("oui", "Oui, le mettre à jour"), ("non", "Pas pour l'instant")))
    col_suggestions = titre("Nos suggestions") + sa + sb + sc + sd + se

    page_b = colonnes(col_pizzas + deco("pizza", "a"), col_suite + deco("verre", "c"), col_ancien + deco("gateau", "b"), col_suggestions)
    return [page_a, page_b]


CSS = """
/* ---------- Pages « mode d'emploi, points à confirmer, suggestions » ---------- */
.page-notes .col{padding-bottom:3mm}
.page-notes .deco{min-height:0}
.etiquette{align-self:center;margin:-3mm 0 5.5mm;padding:1.6mm 4.5mm;white-space:nowrap;border-radius:99mm;background:var(--rouge);color:#fff;
  font-weight:700;font-size:10.2pt;letter-spacing:.03em;text-transform:uppercase;text-align:center}
.note{margin:1mm 0 3mm;font-size:12pt;line-height:1.36}
.etapes{margin:0;padding:0;list-style:none;counter-reset:etape}
.etapes li{position:relative;padding:0 0 2.6mm 10.5mm;font-size:11.8pt;line-height:1.34}
.etapes li::before{counter-increment:etape;content:counter(etape);position:absolute;left:0;top:.3mm;width:7.4mm;height:7.4mm;border-radius:50%;
  background:var(--noir);color:var(--jaune);font-weight:700;font-size:11.5pt;display:grid;place-items:center}
.encadre{margin:1.5mm 0 0;padding:3mm 3.5mm;border:.5mm solid var(--rouge);border-radius:2.5mm;font-size:11.4pt;line-height:1.34}
.encadre b{color:var(--rouge)}
.fait{margin:1mm 0 2.5mm;padding:0 0 0 5mm;font-size:11.6pt;line-height:1.34}
.fait li{margin-bottom:1.5mm;padding-left:.5mm}
.fait li::marker{color:var(--rouge)}
.sous-titre{margin:-.6mm 0 1mm;text-align:center;font-size:10.4pt;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--rouge)}
.q{padding:1.3mm 0 3mm;border-bottom:.3mm dotted #999}
.q:last-of-type{border-bottom:0}
.q-tete{display:flex;align-items:center;gap:2.4mm;margin-bottom:1.3mm}
.q-num{flex:0 0 auto;min-width:7.2mm;height:7.2mm;padding:0 1.6mm;border-radius:2mm;background:var(--noir);color:var(--jaune);font-weight:700;
  font-size:11.8pt;display:inline-grid;place-items:center}
.q-titre{font-weight:700;font-size:13.6pt;line-height:1.2}
.q p{margin:0 0 1.6mm;font-size:11.5pt;line-height:1.35}
.q p.serre{margin:2.2mm 0 0}
.q em{font-style:normal;color:var(--rouge);font-weight:400}
.nom-lu{font-weight:700;font-size:12pt;margin:2.4mm 0 0}
.choix{display:flex;flex-wrap:wrap;align-items:flex-end;gap:1.6mm 6mm;font-size:11.5pt;font-weight:600;margin:1.5mm 0 0}
.option{display:inline-flex;align-items:flex-end;gap:1.9mm;line-height:1.2}
.option.large{flex:1 1 30mm}
.coche{flex:0 0 auto;display:inline-block;width:4.6mm;height:4.6mm;border:.4mm solid var(--noir);border-radius:.7mm;background:#fff}
.champ-ligne{flex:1 1 16mm;min-width:16mm;height:6mm;border-bottom:.25mm solid #9a9a9a}
.reponse{margin:.6mm 0 0}
.reponse i{display:block;height:7.4mm;border-bottom:.25mm solid #9a9a9a}
.grille{display:grid;grid-template-columns:1fr auto auto;gap:1.9mm 5mm;align-items:center;font-size:11.4pt;font-weight:600;margin:1.6mm 0 0;line-height:1.22}
.tete-col{font-size:8.6pt;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:#666;text-align:center}
.tete-col.gauche{text-align:left}
.grille .coche,.grille-noms .coche{justify-self:center}
.grille-noms{display:grid;grid-template-columns:auto auto 1fr;gap:1.5mm 4mm;align-items:end;font-size:11.5pt;font-weight:700;margin:1.4mm 0 0}
.grille-noms .champ-ligne{min-width:0}
"""
