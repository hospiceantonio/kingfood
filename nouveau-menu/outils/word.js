// Fabrique la version Word du document à remplir, à partir du contenu préparé par word.py.
// Usage : node outils/word.js word-modele.json KING-FOOD-nouveau-menu-v2-a-completer.docx
//
// Règle unique pour la personne qui remplit : toute case jaune est une case à remplir.
// Les cases jaunes sont de simples cellules de tableau vides : elles se remplissent dans Word,
// WPS Office ou Google Docs, sur ordinateur comme sur téléphone, et à la main une fois imprimées.
const fs = require('fs');
const {
  AlignmentType, BorderStyle, Document, Footer, HeadingLevel, HeightRule, ImageRun, LevelFormat, Packer, PageNumber,
  Paragraph, ShadingType, Table, TableLayoutType, TableRow, TableCell, TextRun, VerticalAlign, WidthType,
} = require('docx');

const [,, entree, sortie] = process.argv;
const m = JSON.parse(fs.readFileSync(entree, 'utf8'));

// Charte du restaurant
const JAUNE = 'FDC40F', ROUGE = 'C8393B', NOIR = '111111', GRIS = '6B6B6B';
const A_REMPLIR = 'FFF0A8';          // jaune pâle des cases à remplir
const POLICE = 'Arial';

// A4 portrait, marges de 1,9 cm : largeur utile en DXA (1 cm = 567 DXA)
const MARGE = 1080, LARGEUR = 11906 - 2 * MARGE;

const fond = couleur => ({ type: ShadingType.CLEAR, color: 'auto', fill: couleur });
const trait = (couleur = 'B5B5B5', taille = 4) => ({ style: BorderStyle.SINGLE, size: taille, color: couleur });
const SANS = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const cadre = t => ({ top: t, bottom: t, left: t, right: t });
const MARGES_CELLULE = { top: 45, bottom: 45, left: 110, right: 110 };

/** « **gras** » dans un texte → suite de TextRun. */
function runs(texte, options = {}) {
  return String(texte).split('**')
    .map((morceau, i) => (morceau ? new TextRun({ ...options, text: morceau, bold: i % 2 === 1 || !!options.bold }) : null))
    .filter(Boolean);
}

function para(texte, options = {}, run = {}) {
  return new Paragraph({ spacing: { before: 0, after: 100 }, ...options, children: runs(texte, run) });
}

/** Petit paragraphe d'espacement : sans lui, deux tableaux qui se suivent fusionneraient dans Word. */
const espace = (apres = 120) => new Paragraph({ spacing: { before: 0, after: apres }, children: [new TextRun({ text: '', size: 4 })] });

function cellule(enfants, largeur, options = {}) {
  return new TableCell({
    width: { size: largeur, type: WidthType.DXA }, margins: MARGES_CELLULE, verticalAlign: VerticalAlign.CENTER,
    ...options, children: Array.isArray(enfants) ? enfants : [enfants],
  });
}

/** Case à remplir : cellule jaune vide. Le texte tapé dedans sera gras et centré. */
function caseARemplir(largeur, options = {}) {
  return cellule(new Paragraph({ alignment: options.gauche ? AlignmentType.LEFT : AlignmentType.CENTER, spacing: { before: 0, after: 0 },
    keepNext: !!options.suite, run: { bold: true, size: 22, font: POLICE } }), largeur, { shading: fond(A_REMPLIR), borders: cadre(trait(NOIR, 6)) });
}

function celluleEntete(texte, largeur, alignement = AlignmentType.CENTER) {
  return cellule(new Paragraph({ alignment: alignement, keepNext: true, spacing: { before: 0, after: 0 },
    children: [new TextRun({ text: texte, bold: true, size: 18, color: JAUNE })] }), largeur, { shading: fond(NOIR) });
}

function tableau(largeurs, lignes, options = {}) {
  return new Table({
    width: { size: largeurs.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: largeurs, layout: TableLayoutType.FIXED,
    borders: { ...cadre(trait()), insideHorizontal: trait(), insideVertical: trait() }, ...options, rows: lignes,
  });
}

const ligne = (cellules, options = {}) => new TableRow({ cantSplit: true, ...options, children: cellules });

// ------------------------------------------------------------------ titres
const titrePartie = (texte, sautDePage = true) => new Paragraph({
  heading: HeadingLevel.HEADING_1, pageBreakBefore: sautDePage, alignment: AlignmentType.CENTER, shading: fond(NOIR),
  children: [new TextRun({ text: texte })],
});
const titreRubrique = texte => new Paragraph({
  heading: HeadingLevel.HEADING_2, alignment: AlignmentType.CENTER, shading: fond(JAUNE), children: [new TextRun({ text: texte.toUpperCase() })],
});
const sousTitre = texte => new Paragraph({
  keepNext: true, spacing: { before: 280, after: 80 }, border: { bottom: trait(ROUGE, 8) },
  children: [new TextRun({ text: texte.toUpperCase(), bold: true, size: 20, color: ROUGE })],
});

// ------------------------------------------------------------------ le menu
function tableauRubrique(r) {
  const deuxPrix = r.formats.length === 2;
  const largeurs = deuxPrix ? [720, LARGEUR - 720 - 2 * 1650, 1650, 1650] : [720, LARGEUR - 720 - 1900, 1900];
  const entete = ligne([celluleEntete('N°', largeurs[0]), celluleEntete('Plat', largeurs[1], AlignmentType.LEFT),
    ...(deuxPrix ? r.formats.map((f, i) => celluleEntete(`${f} (F)`, largeurs[2 + i])) : [celluleEntete('Prix (F)', largeurs[2])])], { tableHeader: true });

  const cellulePlat = (p, format) => {
    const nom = [new TextRun({ text: p.nom, bold: true })];
    if (format) nom.push(new TextRun({ text: ` — ${format.toLowerCase()}` }));
    const contenu = [new Paragraph({ spacing: { before: 0, after: 0 }, children: nom })];
    if (p.desc) contenu.push(new Paragraph({ spacing: { before: 20, after: 0 }, children: [new TextRun({ text: `(${p.desc})`, size: 19, color: ROUGE })] }));
    return cellule(contenu, largeurs[1]);
  };
  const celluleNumero = texte => cellule(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 0 },
    children: [new TextRun({ text: texte, bold: true })] }), largeurs[0]);
  const cellulePrix = (valeur, largeur) => {
    if (!valeur) return caseARemplir(largeur);
    return cellule(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 0 }, children: [new TextRun({ text: valeur, bold: true })] }),
      largeur, { shading: fond(A_REMPLIR), borders: cadre(trait(NOIR, 6)) });
  };
  const hauteur = { height: { value: 420, rule: HeightRule.ATLEAST } };

  const lignes = [entete];
  for (const p of r.plats) {
    const prix = p.prix ? p.prix.split('/').map(x => x.trim()) : [];
    if (deuxPrix) {
      lignes.push(ligne([celluleNumero(String(p.num)), cellulePlat(p), cellulePrix(prix[0], largeurs[2]), cellulePrix(prix[1], largeurs[3])], hauteur));
    } else if (p.formats.length) {
      // deux prix pour ce seul plat : une ligne par format, sous le même numéro
      p.formats.forEach((f, i) => lignes.push(ligne([celluleNumero(i === 0 ? String(p.num) : ''), cellulePlat(i === 0 ? p : { ...p, desc: '' }, f),
        cellulePrix(prix[i], largeurs[2])], hauteur)));
    } else {
      lignes.push(ligne([celluleNumero(String(p.num)), cellulePlat(p), cellulePrix(prix[0], largeurs[2])], hauteur));
    }
  }
  return tableau(largeurs, lignes);
}

function menu() {
  const blocs = [];
  for (const r of m.rubriques) {
    blocs.push(titreRubrique(r.titre));
    if (r.note) blocs.push(para(r.note, { keepNext: true, alignment: AlignmentType.CENTER, spacing: { before: 0, after: 100 } }, { italics: true, size: 20, color: GRIS }));
    blocs.push(tableauRubrique(r), espace(60));
  }
  return blocs;
}

// ------------------------------------------------------------------ les questions
/** Une liste de choix : une petite case jaune par option, où l'on met un X. */
function tableauChoix(options) {
  const largeurs = [560, LARGEUR - 560];
  return tableau(largeurs, options.map((o, i) => {
    const suite = i < options.length - 1;
    return ligne([
      caseARemplir(largeurs[0], { suite }),
      cellule(para(o, { keepNext: suite, spacing: { before: 0, after: 0 } }), largeurs[1], { borders: cadre(SANS) }),
    ], { height: { value: 420, rule: HeightRule.ATLEAST } });
  }), { borders: { ...cadre(SANS), insideHorizontal: SANS, insideVertical: SANS } });
}

/** Une réponse libre : une invite, puis une grande case jaune. */
function reponseLibre(invite) {
  return [
    para(`${invite} :`, { keepNext: true, spacing: { before: 60, after: 50 } }, { italics: true, size: 20, color: GRIS }),
    tableau([LARGEUR], [ligne([caseARemplir(LARGEUR, { gauche: true })], { height: { value: 700, rule: HeightRule.ATLEAST } })]),
  ];
}

function tableauNoms(lignes) {
  const largeurs = [LARGEUR - 1500 - 3400, 1500, 3400];
  return tableau(largeurs, [
    ligne([celluleEntete('Nom lu', largeurs[0], AlignmentType.LEFT), celluleEntete('Bien lu (X)', largeurs[1]), celluleEntete('Sinon, le bon nom', largeurs[2])], { tableHeader: true }),
    ...lignes.map((l, i) => {
      const suite = i < lignes.length - 1;
      return ligne([
        cellule(new Paragraph({ keepNext: suite, spacing: { before: 0, after: 0 }, children: [new TextRun({ text: l.nom, bold: true }),
          ...(l.note ? [new TextRun({ text: ` ${l.note}`, color: ROUGE })] : [])] }), largeurs[0]),
        caseARemplir(largeurs[1], { suite }), caseARemplir(largeurs[2], { gauche: true, suite }),
      ], { height: { value: 440, rule: HeightRule.ATLEAST } });
    }),
  ]);
}

function tableauGrille(lignes, colonnes) {
  const c = 1500, largeurs = [LARGEUR - c * colonnes.length, ...colonnes.map(() => c)];
  return tableau(largeurs, [
    ligne([celluleEntete("Rubrique de l'ancien menu", largeurs[0], AlignmentType.LEFT), ...colonnes.map((t, i) => celluleEntete(`${t} (X)`, largeurs[1 + i]))], { tableHeader: true }),
    ...lignes.map((l, n) => {
      const suite = n < lignes.length - 1;
      return ligne([cellule(para(l, { keepNext: suite, spacing: { before: 0, after: 0 } }), largeurs[0]), ...colonnes.map((_, i) => caseARemplir(largeurs[1 + i], { suite }))],
        { height: { value: 440, rule: HeightRule.ATLEAST } });
    }),
  ]);
}

function blocQuestion(q) {
  const blocs = [
    new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun({ text: `${q.numero}. `, color: ROUGE }), new TextRun({ text: q.titre })] }),
    para(q.intro, { keepNext: true }),
  ];
  for (const e of q.elements) {
    if (e.type === 'choix') blocs.push(tableauChoix(e.options), espace(80));
    else if (e.type === 'texte') blocs.push(...reponseLibre(e.invite), espace(80));
    else if (e.type === 'noms') blocs.push(tableauNoms(e.lignes), espace(80));
    else if (e.type === 'grille') blocs.push(tableauGrille(e.lignes, e.colonnes), espace(80));
    else if (e.type === 'p') blocs.push(para(e.texte, { keepNext: true, spacing: { before: 80, after: 100 } }));
    else throw new Error(`élément inconnu : ${e.type}`);
  }
  return blocs;
}

// ------------------------------------------------------------------ première page
function premierePage() {
  const logo = fs.readFileSync(m.logo);
  const etapes = m.mode_emploi.map(t => new Paragraph({ numbering: { reference: 'etapes', level: 0 }, spacing: { before: 0, after: 110 }, children: runs(t) }));
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 80 },
      children: [new ImageRun({ type: 'png', data: logo, transformation: { width: 118, height: 118 }, altText: { title: 'Logo KING FOOD', description: 'Logo du restaurant KING FOOD', name: 'logo' } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 0 }, children: [new TextRun({ text: 'LE MENU', bold: true, size: 30, color: JAUNE, characterSpacing: 60 })] }),
    new Paragraph({ heading: HeadingLevel.TITLE, alignment: AlignmentType.CENTER, children: [new TextRun({ text: 'KING FOOD' })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 200 }, children: [new TextRun({ text: 'Vous êtes entre de bonnes mains', bold: true })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, shading: fond(ROUGE), spacing: { before: 0, after: 280, line: 340 },
      children: [new TextRun({ text: m.etiquette.toUpperCase(), bold: true, color: 'FFFFFF', size: 22 })] }),
    tableau([LARGEUR], [ligne([cellule([
      new Paragraph({ spacing: { before: 60, after: 160 }, children: [new TextRun({ text: 'Comment remplir ce document', bold: true, size: 28 })] }),
      ...etapes,
    ], LARGEUR, { margins: { top: 160, bottom: 120, left: 240, right: 240 }, verticalAlign: VerticalAlign.TOP })], { cantSplit: false })],
    { borders: { ...cadre(trait(JAUNE, 24)), insideHorizontal: SANS, insideVertical: SANS } }),
    espace(200),
    // la démonstration : à quoi ressemble une case à remplir
    tableau([2600, LARGEUR - 2600], [ligne([caseARemplir(2600), cellule(para('**Voici une case jaune.** Chaque case comme celle-ci attend un prix, un X ou une réponse.',
      { spacing: { before: 0, after: 0 } }), LARGEUR - 2600, { borders: cadre(SANS) })], { height: { value: 560, rule: HeightRule.ATLEAST } })],
    { borders: { ...cadre(SANS), insideHorizontal: SANS, insideVertical: SANS } }),
    espace(200),
    ...m.encadres.map(t => para(t, { spacing: { before: 0, after: 160 } })),
  ];
}

// ------------------------------------------------------------------ assemblage
const nbQuestions = m.groupes.reduce((n, g) => n + g.questions.length, 0);
const enfants = [
  ...premierePage(),
  titrePartie(`1. Le menu : ${m.nb} prix à compléter`),
  para('Tapez le prix de chaque plat dans sa case jaune, en francs CFA. Les plats sont numérotés de 1 à ' + m.nb + '.', { keepNext: true, spacing: { before: 0, after: 60 } }),
  ...menu(),
  titrePartie('2. Corrections déjà faites'),
  para("Voici ce que nous avons corrigé ou décidé en recopiant vos feuilles. Rien n'est à remplir ici, sauf si un choix ne vous convient pas.", { spacing: { before: 0, after: 140 } }),
  ...m.fait.map(t => new Paragraph({ numbering: { reference: 'puces', level: 0 }, spacing: { before: 0, after: 90 }, children: runs(t) })),
  ...reponseLibre(m.fait_invite), espace(80),
  titrePartie(`3. ${nbQuestions} points à confirmer`),
  para('Pour chaque point, mettez un **X** dans la case jaune de votre choix, ou tapez votre réponse dans la grande case jaune.', { spacing: { before: 0, after: 60 } }),
  ...m.groupes.flatMap(g => [sousTitre(g.titre), ...g.questions.flatMap(blocQuestion)]),
  titrePartie(`4. Nos ${m.suggestions.length} suggestions`),
  para('Ces points ne sont pas obligatoires : ce sont des idées pour améliorer le menu. Répondez de la même façon.', { spacing: { before: 0, after: 60 } }),
  ...m.suggestions.flatMap(blocQuestion),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 400, after: 0 }, shading: fond(JAUNE),
    children: [new TextRun({ text: 'Merci ! Enregistrez ce fichier et renvoyez-le par WhatsApp.', bold: true, size: 24 })] }),
];

const doc = new Document({
  creator: 'KING FOOD', title: 'KING FOOD — nouveau menu, version 2 (document à compléter)',
  description: 'Prix et réponses à saisir dans les cases jaunes.',
  styles: {
    default: {
      document: { run: { font: POLICE, size: 22, language: { value: 'fr-FR' } } },
      title: { run: { font: POLICE, size: 60, bold: true, color: NOIR, characterSpacing: 40 }, paragraph: { spacing: { before: 0, after: 60 }, keepNext: true } },
      heading1: { run: { font: POLICE, size: 30, bold: true, color: JAUNE }, paragraph: { spacing: { before: 0, after: 200 }, keepNext: true } },
      heading2: { run: { font: POLICE, size: 27, bold: true, color: NOIR, characterSpacing: 30 }, paragraph: { spacing: { before: 300, after: 110 }, keepNext: true } },
      heading3: { run: { font: POLICE, size: 24, bold: true, color: NOIR }, paragraph: { spacing: { before: 260, after: 70 }, keepNext: true } },
    },
  },
  numbering: { config: [
    { reference: 'etapes', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 460, hanging: 460 } }, run: { bold: true } } }] },
    { reference: 'puces', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 460, hanging: 300 } }, run: { color: ROUGE, bold: true } } }] },
  ] },
  sections: [{
    properties: { page: { margin: { top: MARGE, bottom: MARGE, left: MARGE, right: MARGE } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [`${m.mention} · page `, PageNumber.CURRENT, ' / ', PageNumber.TOTAL_PAGES].map(c => new TextRun({ children: [c], size: 16, color: GRIS })) })] }) },
    children: enfants,
  }],
});

Packer.toBuffer(doc).then(tampon => {
  fs.writeFileSync(sortie, tampon);
  const cases = m.rubriques.reduce((n, r) => n + r.plats.reduce((k, p) => k + (r.formats.length === 2 ? 2 : Math.max(1, p.formats.length)), 0), 0);
  console.log(`${sortie} : ${m.rubriques.length} rubriques, ${m.nb} plats, ${cases} cases de prix, ${nbQuestions} questions, ${m.suggestions.length} suggestions`);
});
