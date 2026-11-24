// Rend menu-a-completer.html en PDF A3 paysage, contrôle le remplissage de chaque colonne
// et relève la position des cases « prix » (pour en faire des champs de saisie).
// Usage : node outils/rendre.js <entrée.html> <sortie.pdf> <champs.json> [dossier-aperçus]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const [,, entree, sortiePdf, sortieChamps, apercus] = process.argv;

(async () => {
  const navigateur = await chromium.launch();
  const page = await navigateur.newPage({ viewport: { width: 1600, height: 1130 } });
  await page.goto('file://' + path.resolve(entree), { waitUntil: 'load' });
  await page.waitForFunction(() => document.body.dataset.pret === '1');   // polices chargées, ajustements faits

  const bilan = await page.evaluate(() => {
    const px2mm = v => Math.round(v * 25.4 / 96 * 10) / 10;
    const colonnes = [...document.querySelectorAll('.col')].map((col, i) => {
      const fixes = [...col.children].filter(e => !e.classList.contains('deco'));
      const decos = [...col.children].filter(e => e.classList.contains('deco'));
      return {
        colonne: i + 1,
        hauteur: px2mm(col.clientHeight),
        contenu: px2mm(fixes.reduce((h, e) => h + e.getBoundingClientRect().height, 0)),
        decors: decos.map(d => px2mm(d.getBoundingClientRect().height)),
        deborde: col.scrollHeight - col.clientHeight > 1,
      };
    });
    const champs = [...document.querySelectorAll('.blanc[data-champ]')].map(b => {
      const feuille = b.closest('.page');
      const pages = [...document.querySelectorAll('.page')];
      const f = feuille.getBoundingClientRect(), r = b.getBoundingClientRect();
      return { nom: b.dataset.champ, libelle: b.dataset.libelle, page: pages.indexOf(feuille),
               x: r.left - f.left, y: r.top - f.top, l: r.width, h: r.height };   // en px CSS (96 dpi)
    });
    const polices = [...new Set([...document.fonts].filter(f => f.status === 'loaded').map(f => `${f.family} ${f.weight}`))];
    return { colonnes, champs, polices };
  });

  if (apercus) {
    fs.mkdirSync(apercus, { recursive: true });
    const feuilles = await page.locator('.page').all();
    for (let i = 0; i < feuilles.length; i++) await feuilles[i].screenshot({ path: path.join(apercus, `page-${i + 1}.png`) });
  }
  await page.emulateMedia({ media: 'print' });
  await page.pdf({ path: sortiePdf, width: '420mm', height: '297mm', printBackground: true, preferCSSPageSize: true,
                   margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  fs.writeFileSync(sortieChamps, JSON.stringify(bilan.champs, null, 1));

  for (const c of bilan.colonnes) {
    console.log(`colonne ${c.colonne} : contenu ${String(c.contenu).padStart(5)} / ${c.hauteur} mm · décor(s) ${c.decors.join(' + ') || '—'} mm${c.deborde ? '  ← DÉBORDE' : ''}`);
  }
  console.log(`${bilan.champs.length} cases prix · polices : ${bilan.polices.join(', ')}`);
  await navigateur.close();
  if (bilan.colonnes.some(c => c.deborde)) process.exit(2);
})().catch(e => { console.error(e); process.exit(1); });
