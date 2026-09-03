# KING FOOD — le menu par code QR

Le code QR imprimé pointe **une fois pour toutes** vers :

**https://hospiceantonio.github.io/kingfood/**

Cette page lit le fichier `menu.json` de ce dépôt. Pour changer le menu, on
remplace `menu.json` — jamais le code QR.

```
index.html, carte.css, carte.js   la page que voient les clients (ne pas modifier)
identite.css                      la charte graphique (couleurs, polices) — un seul fichier
logo.png                          le logo (fond transparent) : page, QR, supports, icônes
menu.json                         ★ LE MENU — le seul fichier à remplacer quand il change
menu.schema.json                  description du format
manifest.webmanifest, icone-*.png « ajouter à l'écran d'accueil » sur téléphone
outils/importer-carte.html        l'outil pour préparer un nouveau menu.json
qr/                               le code QR, les supports d'impression, le générateur
.github/workflows/pages.yml       la publication automatique sur GitHub Pages
```

## Mettre le menu à jour (3 étapes, sans rien installer)

1. Ouvrir **https://hospiceantonio.github.io/kingfood/outils/importer-carte.html**
   et cliquer sur **Charger la carte en ligne**. Le menu apparaît sous forme de texte :

   ```
   ## Burgers | Prix : sandwich / assiette
   44-45 - Chicken Burger | 4000 / 5000
   64-65 - Burger King Food | jambon, viande, fromage, oignon, frites, sauce burger | 5000 / 6000

   ## Boissons
   251 - Coca-Cola | 1000
   ```

   Modifier les prix, ajouter ou retirer des lignes ou des catégories (`##`).
   L'aperçu à droite se met à jour et signale les lignes à corriger. On peut
   aussi coller des lignes venant d'Excel (colonnes Nom, Description, Prix).

2. Quand la vérification est verte, cliquer sur **Télécharger menu.json**.

3. Cliquer sur **Déposer sur GitHub** (ou aller sur
   https://github.com/hospiceantonio/kingfood/upload/main), glisser le fichier
   `menu.json` téléchargé, laisser « Commit directly to the main branch » et
   cliquer sur **Commit changes**.

Une à deux minutes plus tard, le menu est à jour sur tous les téléphones qui
scannent le QR (l'onglet **Actions** du dépôt montre la publication en cours).

> Variante rapide pour un seul prix : sur GitHub, ouvrir `menu.json`, cliquer
> sur le crayon ✏️, corriger, puis **Commit changes**. Attention aux guillemets
> et aux virgules ; en cas de doute, passer par l'outil.

Les coordonnées (téléphones, horaires, réseaux) se modifient dans l'outil,
rubrique « Coordonnées du restaurant », ou directement dans le bloc
`restaurant` de `menu.json`.

## Le code QR (dossier `qr/`)

| Fichier | Usage |
|---|---|
| `qr-carte.svg` | **À donner à l'imprimeur.** Vectoriel, logo au centre, s'agrandit sans perte. |
| `qr-carte.png` | 2 000 px — WhatsApp, Facebook, Instagram, TikTok, Word, Canva… |
| `qr-carte-simple.svg` / `.png` | Version sans logo, lisibilité maximale (très petits formats). |
| `qr-cartes-de-table-a6.pdf` | 4 cartes A6 par feuille A4, prêtes à imprimer et découper. |
| `qr-affiche-a4.pdf` | Affiche pour l'entrée, le comptoir ou la caisse. |
| `impression-*.html` | Les mêmes supports, modifiables et imprimables depuis un navigateur (Ctrl+P). |
| `generer-qr.py` | Regénère les QR (nouveau logo, ou **uniquement** si l'adresse change un jour). |

Conseils d'impression : fond clair, code d'au moins 3 cm de côté sur une table,
6 cm ou plus sur une affiche, et garder une marge blanche autour du code.

## Mise en ligne (une seule fois)

Le dépôt s'appelle `kingfood`, donc GitHub Pages le publie à
`https://hospiceantonio.github.io/kingfood/` — l'adresse du QR.

1. Sur GitHub : **Settings → Pages → Build and deployment → Source** : choisir
   **GitHub Actions** (le workflow tente aussi de l'activer tout seul).
2. Onglet **Actions** : le workflow « Publier le menu sur GitHub Pages » doit
   être vert. S'il a échoué avant l'étape 1, l'ouvrir et cliquer **Run workflow**.
3. Ouvrir l'adresse sur un téléphone, puis **scanner le QR** depuis un PDF
   affiché à l'écran : le menu doit s'ouvrir. Imprimer seulement après.

## Et si l'adresse change un jour ?

Le QR imprimé continuera de fonctionner tant que `hospiceantonio.github.io/kingfood/`
répond. Si le restaurant prend un nom de domaine (ex. `kingfood.bj`), il suffit
de laisser à cette adresse une page qui redirige vers le nouveau site : les
cartes déjà imprimées restent valables. Pour de nouvelles impressions :

```
pip install segno pillow zxing-cpp
python3 qr/generer-qr.py https://kingfood.bj/menu/
```
