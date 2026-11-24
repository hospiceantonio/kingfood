# Nouveau menu KING FOOD (projet, prix à compléter)

Le nouveau menu, transcrit des feuilles manuscrites du restaurant (24 novembre 2026)
et mis en page comme l'ancien menu imprimé : A3 paysage, quatre colonnes, cartouches
jaunes, plats numérotés, descriptions en rouge.

| Fichier | Rôle |
|---|---|
| `KING-FOOD-nouveau-menu-prix-a-completer.pdf` | **Le document à compléter.** Chaque prix est une case vide : on la remplit à l'écran (champ de saisie) ou à la main après impression. |
| `nouveau-menu.txt` | Le contenu : une ligne par plat, `Nom \| Description \| Prix`. C'est ici qu'on corrige un plat ou qu'on saisit les prix. |
| `outils/composer.py` | Met en page `nouveau-menu.txt` (répartition des rubriques par colonne dans `PLAN`). |
| `outils/rendre.js` | Rend la page en PDF et vérifie qu'aucune colonne ne déborde. |
| `outils/champs.py` | Pose un champ de saisie sur chaque case « prix ». |
| `polices-menu.css` | Polices embarquées (Amatic SC, Cabin, Sacramento, Montserrat — licence OFL). |

## Régénérer le PDF

```
pip install pymupdf            # Playwright (Chromium) doit aussi être installé
python3 outils/composer.py
node outils/rendre.js menu-a-completer.html brouillon.pdf champs.json
python3 outils/champs.py brouillon.pdf champs.json KING-FOOD-nouveau-menu-prix-a-completer.pdf
```

## Saisir les prix

Dans `nouveau-menu.txt`, le prix est le dernier champ de la ligne :

```
Salade César | laitue, tranches de poulet, parmesan, ail, jambon | 3500
Poulet KFC | | @Complet / Demi | 7000 / 3500
```

Un prix renseigné s'imprime à la place de la case vide. Ce dossier est un document de
travail : il n'est pas publié sur le site du menu. Une fois les prix validés, le contenu
sera repris dans `menu.json` (le menu en ligne ouvert par le code QR).
