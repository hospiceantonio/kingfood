"""Page « Mode d'emploi, points à confirmer et suggestions », ajoutée à la suite du menu
dans le PDF envoyé au restaurant. Les numéros de plats cités sont retrouvés par leur nom
dans nouveau-menu.txt : ils restent justes si la numérotation change. `deco` est la fonction
de composer.py qui dessine un disque illustré.

Chaque case à cocher et chaque ligne de réponse porte un attribut data-champ : rendre.js
relève sa position et champs.py en fait un champ de saisie du PDF."""
import html

# Rubriques de l'ancien menu dont les feuilles manuscrites ne parlent pas
RUBRIQUES_ANCIEN_MENU = [
    "Chawarmas", "Pizzas", "Sauces gluantes et liquides", "Plats africains, suggestions du chef",
    "Accompagnements", "Crêpes, gaufres, gâteaux, glaces", "Cocktails, jus et boissons", "Boissons chaudes", "Chicha",
]

e = html.escape


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


def rendu_page(rubriques, tete, mention, folio, deco):
    plats = [p for r in rubriques for p in r["plats"]]
    nb = len(plats)

    def num(nom):
        trouves = [p["num"] for p in plats if p["nom"] == nom]
        if not trouves:
            raise SystemExit(f"questions.py : plat introuvable dans nouveau-menu.txt → {nom}")
        return trouves

    def n(nom):
        return f'n°&nbsp;{num(nom)[0]}'

    deux_prix = [str(p["num"]) for p in plats if p["formats"]]
    sans_desc = sum(1 for p in plats if not p["desc"])
    viandes_rouges = next(r for r in rubriques if r["titre"] == "Viandes rouges")["plats"][0]
    crevettes, rouleaux = num("Crevettes sautées à l'ail"), [num("Rouleaux aux fromages")[0], num("Rouleau aux fromages")[0]]

    # ---------------------------------------------------------------- colonne 1
    col1 = tete + '<div class="etiquette">Projet à compléter et à nous renvoyer</div>' + titre("Mode d'emploi") + f'''
<p class="note">Voici le projet de votre nouveau menu : les {nb} plats de vos feuilles, numérotés de 1 à {nb}, pages 1 et 2.</p>
<ol class="etapes">
  <li><b>Les prix.</b> Écrivez le prix de chaque plat dans la case placée avant le «&nbsp;F&nbsp;». À l'écran, cliquez dans la case&nbsp;; sur papier, écrivez à la main.</li>
  <li><b>Deux prix.</b> Les poulets n°&nbsp;{", ".join(deux_prix[:-1])} et {deux_prix[-1]} ont deux cases&nbsp;: Complet et Demi.</li>
  <li><b>Les questions.</b> Répondez aux points de cette page&nbsp;: une case à cocher ou quelques mots suffisent.</li>
  <li><b>Le retour.</b> Renvoyez ce document rempli, ou une photo nette de chacune des trois pages.</li>
</ol>
<p class="note fin">Dès votre retour, nous préparons le menu définitif, prêt à imprimer.</p>''' + deco("pilon", "a")

    # ---------------------------------------------------------------- colonne 2
    fait = titre("Déjà fait") + f'''
<ul class="fait">
  <li>L'orthographe est corrigée, sans changer les plats.</li>
  <li>«&nbsp;Lapin à la moutarde&nbsp;», barré sur votre feuille, n'est pas repris.</li>
  <li>«&nbsp;Sandwich libanais&nbsp;» devient «&nbsp;Sandwichs&nbsp;»&nbsp;: le mot «&nbsp;libanais&nbsp;» était raturé.</li>
  <li>La feuille «&nbsp;Suite viande rouge brochette&nbsp;» devient la rubrique «&nbsp;Brochettes &amp; grillades&nbsp;».</li>
  <li>Les plats sont numérotés de 1 à {nb}, dans l'ordre de vos rubriques.</li>
  <li>Des dessins remplacent pour l'instant les photos de l'ancien menu.</li>
</ul>
<p class="note">Un de ces choix ne vous convient pas&nbsp;? Dites-le ici&nbsp;:</p>''' + reponse("fait_remarques", "Remarques sur ce qui a déjà été fait", 2)

    def nom_lu(cle, nom, note=""):
        return (f'<div class="nom-lu">{n(nom)} — {e(nom)}{f" <em>{e(note)}</em>" if note else ""}</div>'
                f'<div class="choix"><span class="option">{coche(f"q1_{cle}_ok", f"{nom} : bien lu")}Bien lu</span>'
                f'<span class="option large">Sinon&nbsp;:{ligne(f"q1_{cle}_nom", f"Bon nom à la place de {nom}")}</span></div>')

    q1 = bloc(1, "Trois noms difficiles à lire",
              '<p>Avons-nous bien lu&nbsp;? Cochez, ou écrivez le bon nom.</p>'
              + nom_lu("farfalle", "Farfalle King Food", "(écrit « Fafal »)")
              + nom_lu("malake", "Sandwich malaké végétarien")
              + nom_lu("venito", "Panini Vénito"))
    q2 = bloc(2, f'Poulet strogonof (n°\u00a0{num("Poulet strogonof")[0]})',
              f'<p>Votre feuille lui donne la description «&nbsp;filet de bœuf, sauce aux poivres verts&nbsp;», la même que le steak {n("Steak aux poivres verts")}. '
              'Quelle est la bonne description&nbsp;?</p>' + reponse("q2_description", "Bonne description du poulet strogonof", 2))
    col2 = fait + titre("À confirmer") + q1 + q2

    # ---------------------------------------------------------------- colonne 3
    q3 = bloc(3, "Viandes rouges",
              f'<p>La rubrique commence en haut d\'une feuille, sans titre, par «&nbsp;{e(viandes_rouges["nom"])}&nbsp;» (n°&nbsp;{viandes_rouges["num"]}). '
              'Manque-t-il une feuille avant&nbsp;?</p>'
              + choix("q3", "Feuille manquante avant les viandes rouges", ("non", "Non, la liste est complète"), ("oui", "Oui, nous vous l'envoyons")))
    q4 = bloc(4, "Plats en double",
              f'<p>«&nbsp;Crevettes sautées à l\'ail&nbsp;» figure aux n°&nbsp;{crevettes[0]} et {crevettes[1]}&nbsp;; '
              f'«&nbsp;Rouleaux aux fromages&nbsp;» aux n°&nbsp;{rouleaux[0]} et {rouleaux[1]}.</p>'
              + choix("q4", "Plats en double", ("deux", "Garder les deux fois"), ("un", "Garder une seule fois"))
              + '<p class="serre">Dans quelle rubrique les garder&nbsp;?</p>' + reponse("q4_rubrique", "Rubrique où garder les plats en double", 1))
    grille = '<div class="grille"><span></span><span class="tete-col">Garder</span><span class="tete-col">Supprimer</span>' + "".join(
        f'<span>{e(r)}</span>{coche(f"q5_{i + 1}_garder", f"{r} : garder")}{coche(f"q5_{i + 1}_supprimer", f"{r} : supprimer")}'
        for i, r in enumerate(RUBRIQUES_ANCIEN_MENU)) + '</div>'
    q5 = bloc(5, "Rubriques de l'ancien menu",
              '<p>Vos feuilles ne parlent pas de ces rubriques. Faut-il les garder comme avant, ou les supprimer&nbsp;?</p>' + grille
              + '<p class="serre">Si des prix y changent, indiquez-les ici&nbsp;:</p>' + reponse("q5_prix", "Prix qui changent dans les rubriques de l'ancien menu", 3))
    col3 = titre("À confirmer (suite)") + q3 + q4 + q5

    # ---------------------------------------------------------------- colonne 4
    s1 = bloc("A", "Accompagnements",
              '<p>L\'ancien menu les listait&nbsp;: riz, frites, aloco, attiéké, pâte, couscous… Nous suggérons de les rappeler, '
              'en précisant s\'ils sont compris dans le prix des plats.</p>'
              + '<div class="choix"><span class="option">' + coche("sA_compris", "Accompagnements : compris dans le prix") + 'Compris dans le prix</span>'
              + '<span class="option large">' + coche("sA_supplement", "Accompagnements : en supplément") + 'En supplément&nbsp;:'
              + ligne("sA_prix", "Prix de l'accompagnement en supplément") + 'F</span></div>'
              + '<p class="serre">Liste des accompagnements à jour&nbsp;:</p>' + reponse("sA_liste", "Liste des accompagnements", 2))
    s2 = bloc("B", "Descriptions",
              f'<p>{sans_desc} plats sur {nb} n\'ont pas de description. Une ligne courte aide le client à choisir, par exemple pour '
              '«&nbsp;Zinger burger&nbsp;», «&nbsp;Sandwich samaké&nbsp;», «&nbsp;Crevettes à l\'indienne&nbsp;» ou «&nbsp;Poisson strogonof&nbsp;».</p>'
              + choix("sB", "Descriptions manquantes", ("ainsi", "Laisser ainsi"), ("envoi", "Nous vous les envoyons")))
    s3 = bloc("C", "Photos des plats",
              '<p>L\'ancien menu montrait des photos&nbsp;; ce projet utilise des dessins. Avec six à huit photos nettes de vos plats, '
              'nous pouvons revenir à des photos.</p>'
              + choix("sC", "Photos des plats", ("dessins", "Garder les dessins"), ("photos", "Nous envoyons des photos")))
    s4 = bloc("D", "Menu en ligne (code QR)",
              '<p>Le code QR ouvre encore l\'ancien menu. Une fois les prix validés, le menu en ligne peut être mis à jour en même temps&nbsp;: '
              'le code QR déjà imprimé ne change pas.</p>'
              + choix("sD", "Menu en ligne", ("oui", "Oui, le mettre à jour"), ("non", "Pas pour l'instant")))
    col4 = titre("Nos suggestions") + s1 + s2 + s3 + s4 + deco("pates", "c")

    cols = "".join(f'<div class="col">{c}</div>' for c in (col1, col2, col3, col4))
    return (f'<div class="page page-notes"><div class="filet-jaune"></div><div class="cadre">{cols}</div>'
            f'<div class="mention">{e(mention)}</div><div class="folio">{folio}</div></div>')


CSS = """
/* ---------- Page « mode d'emploi, points à confirmer, suggestions » ---------- */
.page-notes .col{padding-bottom:3mm}
.etiquette{align-self:center;margin:-3mm 0 5.5mm;padding:1.6mm 4.5mm;border-radius:99mm;background:var(--rouge);color:#fff;
  font-weight:700;font-size:10.6pt;letter-spacing:.03em;text-transform:uppercase;text-align:center}
.note{margin:1mm 0 3mm;font-size:12.4pt;line-height:1.38}
.note.fin{margin-top:3mm;font-weight:700}
.etapes{margin:0;padding:0;list-style:none;counter-reset:etape}
.etapes li{position:relative;padding:0 0 3.4mm 10.5mm;font-size:12.4pt;line-height:1.38}
.etapes li::before{counter-increment:etape;content:counter(etape);position:absolute;left:0;top:.3mm;width:7.4mm;height:7.4mm;border-radius:50%;
  background:var(--noir);color:var(--jaune);font-weight:700;font-size:11.5pt;display:grid;place-items:center}
.fait{margin:1mm 0 2.5mm;padding:0 0 0 5mm;font-size:11.8pt;line-height:1.36}
.fait li{margin-bottom:1.5mm;padding-left:.5mm}
.fait li::marker{color:var(--rouge)}
.q{padding:1.4mm 0 3.4mm;border-bottom:.3mm dotted #999}
.q:last-child{border-bottom:0}
.q-tete{display:flex;align-items:center;gap:2.4mm;margin-bottom:1.4mm}
.q-num{flex:0 0 auto;min-width:7.2mm;height:7.2mm;padding:0 1.6mm;border-radius:2mm;background:var(--noir);color:var(--jaune);font-weight:700;
  font-size:11.8pt;display:inline-grid;place-items:center}
.q-titre{font-weight:700;font-size:14pt;line-height:1.2}
.q p{margin:0 0 1.8mm;font-size:11.8pt;line-height:1.37}
.q p.serre{margin:2.4mm 0 0}
.q em{font-style:normal;color:var(--rouge);font-weight:400}
.nom-lu{font-weight:700;font-size:12.2pt;margin:2.6mm 0 0}
.choix{display:flex;flex-wrap:wrap;align-items:flex-end;gap:1.8mm 6mm;font-size:11.8pt;font-weight:600;margin:1.6mm 0 0}
.option{display:inline-flex;align-items:flex-end;gap:1.9mm;line-height:1.2}
.option.large{flex:1 1 30mm}
.coche{flex:0 0 auto;display:inline-block;width:4.6mm;height:4.6mm;border:.4mm solid var(--noir);border-radius:.7mm;background:#fff}
.champ-ligne{flex:1 1 16mm;min-width:16mm;height:6mm;border-bottom:.25mm solid #9a9a9a}
.reponse{margin:.6mm 0 0}
.reponse i{display:block;height:7.6mm;border-bottom:.25mm solid #9a9a9a}
.grille{display:grid;grid-template-columns:1fr auto auto;gap:1.7mm 5mm;align-items:center;font-size:11.8pt;font-weight:600;margin:1.6mm 0 0}
.grille .tete-col{font-size:8.8pt;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:#666;text-align:center}
.grille .coche{justify-self:center}
"""
