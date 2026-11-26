# Nouveau menu KING FOOD (projet, version 2, prix à compléter)

Le nouveau menu du restaurant, mis en page comme l'ancien menu imprimé : A3 paysage,
quatre colonnes, cartouches jaunes, plats numérotés, descriptions en rouge.

Sources reçues du restaurant :

- 24 novembre 2026 — 7 feuilles manuscrites : petits déjeuners, entrées, sandwichs, pâtes,
  fruits de mer, viandes, brochettes, nouveautés du chef, menu enfants ;
- 26 novembre 2026 — 10 feuilles manuscrites : pizzas, cocktails, jus, boissons, glaces,
  crêpes, gaufres, gâteaux, boissons chaudes, chicha ;
- 26 novembre 2026 — 2 captures d'écran d'un menu noir et or : chawarmas et burgers, avec
  leurs prix (la capture des burgers est coupée à droite).

| Fichier | Rôle |
|---|---|
| `KING-FOOD-nouveau-menu-v2-prix-a-completer.pdf` | **Le document à envoyer au restaurant** (6 pages). Pages 1 à 4 : le menu, 25 rubriques et 248 plats ; chaque prix inconnu est une case vide à remplir à l'écran (champ de saisie) ou à la main. Pages 5 et 6 : mode d'emploi, corrections déjà faites, 17 points à confirmer et 5 suggestions, avec cases à cocher et lignes de réponse. |
| `nouveau-menu.txt` | Le contenu : une ligne par plat, `Nom \| Description \| Prix`. C'est ici qu'on corrige un plat ou qu'on saisit les prix. Les rubriques y sont dans l'ordre de lecture du menu. |
| `outils/composer.py` | Met en page `nouveau-menu.txt` ; la répartition des rubriques par colonne est dans `PLAN`. |
| `outils/questions.py` | Le texte des pages 5 et 6. Les numéros de plats cités sont retrouvés par leur nom. |
| `outils/mesurer.js` | Mesure la hauteur de chaque rubrique, pour répartir les colonnes dans `PLAN`. |
| `outils/rendre.js` | Rend la page en PDF et refuse une colonne qui déborde. |
| `outils/champs.py` | Pose un champ de saisie sur chaque case : prix, réponses, cases à cocher. |
| `polices-menu.css` | Polices embarquées (Amatic SC, Cabin, Sacramento, Montserrat — licence OFL). |

## Régénérer le PDF

```
pip install pymupdf            # Playwright (Chromium) doit aussi être installé
python3 outils/composer.py     # --sans-questions : le menu seul (4 pages)
node outils/rendre.js menu-a-completer.html brouillon.pdf champs.json
python3 outils/champs.py brouillon.pdf champs.json KING-FOOD-nouveau-menu-v2-prix-a-completer.pdf
```

Après avoir ajouté ou retiré des plats, vérifier la répartition :

```
python3 outils/composer.py --mesure && node outils/mesurer.js menu-a-completer.html
```

puis ajuster `PLAN` dans `composer.py`. Le script refuse un `PLAN` qui oublie un plat ou
dont les numéros ne se suivent pas dans l'ordre de lecture.

## Format de `nouveau-menu.txt`

```
## Burgers | @Sandwich / Assiette              ← rubrique à deux colonnes de prix
Chicken burger | viande chicken, choux, laitue | 3500 / 4000
Fish burger | laitue, tomate, poisson |        ← prix vides : deux cases à compléter

## Chawarmas | Cornichon au choix.             ← note affichée sous le titre
Chawarma poulet | choux, frites, crème d'ail | 2500

## Brochettes & grillades
Poulet KFC | | @Complet / Demi                 ← deux prix pour ce seul plat
```

Un prix renseigné s'imprime à la place de la case vide. Les champs du PDF portent le nom
de la rubrique et du plat (`prix__pizzas__reine__grande`), pas son numéro : un PDF rempli
reste lisible même si la numérotation change ensuite.

Ce dossier est un document de travail : il n'est pas publié sur le site du menu. Une fois
les prix validés, le contenu sera repris dans `menu.json` (le menu en ligne ouvert par le
code QR).
