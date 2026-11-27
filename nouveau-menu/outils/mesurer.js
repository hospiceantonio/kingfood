// Mesure la hauteur de chaque rubrique (et le cumul plat par plat) dans une colonne du menu,
// pour répartir les rubriques entre les colonnes dans PLAN (composer.py).
// Usage : python3 outils/composer.py --mesure && node outils/mesurer.js menu-a-completer.html
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const navigateur = await chromium.launch();
  const page = await navigateur.newPage({ viewport: { width: 1600, height: 1130 } });
  await page.goto('file://' + path.resolve(process.argv[2]), { waitUntil: 'load' });
  await page.waitForFunction(() => document.body.dataset.pret === '1');
  const mesures = await page.evaluate(() => {
    const mm = v => Math.round(v * 25.4 / 96 * 10) / 10;
    const colonne = document.querySelector('.col');
    return { utile: mm(colonne.clientHeight - parseFloat(getComputedStyle(colonne).paddingBottom)),
      rubriques: [...document.querySelectorAll('.rubrique')].map(r => {
        const haut = r.getBoundingClientRect().top;
        const plats = [...r.querySelectorAll('.plat')];
        return { titre: r.dataset.titre, total: mm(r.getBoundingClientRect().height),
                 avant: mm(plats[0].getBoundingClientRect().top - haut),          // titre, note, en-têtes
                 cumul: plats.map(p => mm(p.getBoundingClientRect().bottom - haut)) };
      }) };
  });
  console.log(`hauteur utile d'une colonne : ${mesures.utile} mm`);
  for (const r of mesures.rubriques) {
    console.log(`${String(r.total).padStart(6)} mm  ${r.titre} (${r.cumul.length} plats, en-tête ${r.avant} mm)`);
    if (r.total > mesures.utile * 0.75) console.log('           cumul : ' + r.cumul.map((c, i) => `${i + 1}:${Math.round(c)}`).join(' '));
  }
  await navigateur.close();
})().catch(e => { console.error(e); process.exit(1); });
