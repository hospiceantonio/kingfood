/* =========================================================
   LE MENU KING FOOD — page scannée par le code QR.

   Tout le menu vient de menu.json, chargé à l'affichage.
   Remplacer menu.json suffit à changer la carte : ni cette page,
   ni le code QR imprimé n'ont besoin d'être refaits.
   ========================================================= */

const SOURCE = 'menu.json';
const CACHE_KEY = 'kingfood.carte.v2';   // dernière copie vue : affichée aussitôt, puis rafraîchie

let menu = null;
let salleCourante = null;
let categorieCourante = 'all';
let recherche = '';

/* ---------- Utilitaires ---------- */

function echapper(txt){
  return String(txt).replace(/[&<>"']/g, c => (
    { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]
  ));
}

/* Prix stockés « 3500 » ou « 5000 / 6500 » → « 3500 F » / « 5000 F / 6500 F ». */
function formaterPrix(prix, devise){
  return String(prix).split('/').map(v => `${v.trim()} ${devise}`).join(' / ');
}

/* Pour la recherche : sans accents, sans casse. */
function normaliser(txt){
  return String(txt).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
}

/* Surligne le terme cherché dans un texte déjà échappé. */
function surligner(texteEchappe, terme){
  if (!terme) return texteEchappe;
  const source = normaliser(texteEchappe);
  const cible = normaliser(terme);
  let sortie = '', depart = 0, i;
  while ((i = source.indexOf(cible, depart)) !== -1){
    sortie += texteEchappe.slice(depart, i)
            + '<mark>' + texteEchappe.slice(i, i + cible.length) + '</mark>';
    depart = i + cible.length;
  }
  return sortie + texteEchappe.slice(depart);
}

/* ---------- Rendu ---------- */

function salle(){
  return menu.salles.find(s => s.id === salleCourante) || menu.salles[0];
}

function afficherOngletsSalle(){
  const el = document.getElementById('rooms');
  // Une seule carte : les onglets n'apportent rien.
  el.hidden = menu.salles.length < 2;
  if (el.hidden) return;
  el.innerHTML = menu.salles.map(s => `
    <button type="button" class="room-tab" role="tab"
            data-salle="${echapper(s.id)}"
            aria-selected="${s.id === salleCourante}">${echapper(s.label)}</button>
  `).join('');
  el.querySelectorAll('.room-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      salleCourante = btn.dataset.salle;
      categorieCourante = 'all';
      afficherOngletsSalle();
      afficherCategories();
      afficherCarte();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });
}

function afficherCategories(){
  const el = document.getElementById('cats');
  const cats = salle().categories;
  el.innerHTML = [{ id:'all', label:'Tout le menu' }, ...cats].map(c => `
    <button type="button" class="cat-pill${c.id === categorieCourante ? ' active' : ''}"
            data-cat="${echapper(c.id)}">${echapper(c.label)}</button>
  `).join('');
  el.querySelectorAll('.cat-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      categorieCourante = btn.dataset.cat;
      afficherCategories();
      afficherCarte();
      btn.scrollIntoView({ inline:'center', block:'nearest', behavior:'smooth' });
    });
  });
}

function correspond(it, cible){
  return normaliser(it.nom).includes(cible)
      || (it.description && normaliser(it.description).includes(cible))
      || (it.numero && String(it.numero).split('-').includes(cible));   // « 45 » trouve le plat 45
}

function afficherCarte(){
  const el = document.getElementById('menu');
  const devise = (menu.restaurant && menu.restaurant.devise) || 'F';
  const terme = recherche.trim();
  const cible = normaliser(terme);

  let cats = salle().categories;

  // Une recherche en cours passe outre le filtre de catégorie :
  // le client cherche un plat, pas une rubrique.
  if (cible){
    cats = cats
      .map(c => ({ ...c, items: c.items.filter(it => correspond(it, cible)) }))
      .filter(c => c.items.length);
  } else if (categorieCourante !== 'all'){
    cats = cats.filter(c => c.id === categorieCourante);
  }

  if (!cats.length){
    el.innerHTML = `<p class="empty"><strong>Aucun résultat pour « ${echapper(terme)} »</strong>
      Essayez un autre mot ou un numéro de plat, ou parcourez les catégories ci-dessus.</p>`;
    return;
  }

  el.innerHTML = cats.map(c => `
    <section class="cat-block" id="cat-${echapper(c.id)}">
      <h2 class="cat-title">${echapper(c.label)}</h2>
      ${c.note ? `<p class="cat-note">${echapper(c.note)}</p>` : ''}
      <div class="cat-items">
        ${c.items.map(it => `
          <div class="item">
            <div class="item-main">
              <div class="item-name">${it.numero ? `<span class="item-num">${echapper(it.numero)}</span>` : ''}${surligner(echapper(it.nom), terme)}</div>
              ${it.description
                ? `<div class="item-desc">${surligner(echapper(it.description), terme)}</div>`
                : ''}
            </div>
            ${it.prix ? `<div class="item-price">${echapper(formaterPrix(it.prix, devise))}</div>` : ''}
          </div>
        `).join('')}
      </div>
    </section>
  `).join('');
}

function afficherEnTete(){
  const r = menu.restaurant || {};
  if (r.nom){
    document.title = `Le Menu — ${r.nom}`;
    document.getElementById('nomRestaurant').textContent = r.nom;
  }
  const sous = document.getElementById('sousTitre');
  sous.hidden = !r.sousTitre;
  sous.textContent = r.sousTitre || '';
}

function afficherPiedDePage(horsLigne){
  const r = menu.restaurant || {};

  const maj = document.getElementById('maj');
  const date = menu.miseAJour
    ? new Date(menu.miseAJour + 'T00:00:00').toLocaleDateString('fr-FR',
        { day:'numeric', month:'long', year:'numeric' })
    : null;
  maj.textContent = horsLigne
    ? 'Menu affiché hors connexion — reconnectez-vous pour la dernière version.'
    : (date ? `Menu mis à jour le ${date}` : '');

  document.getElementById('footInfo').innerHTML = [
    r.adresse    ? `<div>${echapper(r.adresse)}</div>` : '',
    r.horaires   ? `<div>${echapper(r.horaires)}</div>` : '',
    r.telephones ? `<div class="tel">${echapper(r.telephones)}</div>`
                 : (r.telephone ? `<div><a href="tel:${echapper(r.telephone.replace(/\s/g,''))}">${echapper(r.telephone)}</a></div>` : ''),
    r.email      ? `<div><a href="mailto:${echapper(r.email)}">${echapper(r.email)}</a></div>` : '',
    r.reseaux    ? `<div>${echapper(r.reseaux)}</div>` : ''
  ].join('');

  const mention = document.getElementById('mention');
  mention.hidden = !r.mention;
  mention.textContent = r.mention || '';

  const ICONES = {
    tel: '<path d="M4 4h4l2 5-2.5 1.5a12 12 0 0 0 6 6L15 14l5 2v4a1 1 0 0 1-1 1A17 17 0 0 1 3 5a1 1 0 0 1 1-1z"/>',
    wa:  '<path d="M12 3a9 9 0 0 0-7.7 13.6L3 21l4.5-1.2A9 9 0 1 0 12 3z"/><path d="M8.5 9.5c0 3 2 5 5 5"/>',
    map: '<path d="M12 21s7-6.3 7-11a7 7 0 1 0-14 0c0 4.7 7 11 7 11z"/><circle cx="12" cy="10" r="2.6"/>'
  };
  const actions = [
    r.telephone && { href:`tel:${r.telephone.replace(/\s/g,'')}`, ico:ICONES.tel, txt:'Appeler' },
    r.whatsapp  && { href:`https://wa.me/${r.whatsapp}`, ico:ICONES.wa, txt:'WhatsApp', ext:true },
    r.maps      && { href:r.maps, ico:ICONES.map, txt:'Itinéraire', ext:true }
  ].filter(Boolean);

  const barre = document.getElementById('actionbar');
  barre.hidden = !actions.length;
  document.body.classList.toggle('sans-actions', !actions.length);
  barre.innerHTML = actions.map(a => `
    <a class="action" href="${echapper(a.href)}"${a.ext ? ' target="_blank" rel="noopener"' : ''}>
      <svg viewBox="0 0 24 24" aria-hidden="true">${a.ico}</svg>
      <span>${a.txt}</span>
    </a>
  `).join('');
}

/* ---------- Recherche ---------- */

function brancherRecherche(){
  const champ = document.getElementById('search');
  const effacer = document.getElementById('searchClear');

  champ.addEventListener('input', () => {
    recherche = champ.value;
    effacer.hidden = !recherche;
    afficherCarte();
  });

  effacer.addEventListener('click', () => {
    champ.value = '';
    recherche = '';
    effacer.hidden = true;
    afficherCarte();
    champ.focus();
  });

  // Entrée referme le clavier du téléphone au lieu d'envoyer un formulaire.
  champ.addEventListener('keydown', e => { if (e.key === 'Enter') champ.blur(); });
}

/* ---------- Démarrage ---------- */

let rechercheBranchee = false;

function afficher(data, horsLigne){
  menu = data;
  if (!menu.salles.some(s => s.id === salleCourante)) salleCourante = menu.salles[0].id;
  afficherEnTete();
  afficherOngletsSalle();
  afficherCategories();
  afficherCarte();
  afficherPiedDePage(horsLigne);
  if (!rechercheBranchee){ brancherRecherche(); rechercheBranchee = true; }
}

function menuValide(m){
  return m && Array.isArray(m.salles) && m.salles.length > 0;
}

(async function demarrer(){
  // 1. Affichage immédiat de la dernière copie vue sur ce téléphone, s'il y en a une :
  //    le client n'attend pas le réseau pour lire le menu.
  let texteCopie = null;
  try {
    texteCopie = localStorage.getItem(CACHE_KEY);
    const copie = texteCopie && JSON.parse(texteCopie);
    if (menuValide(copie)) afficher(copie, false); else texteCopie = null;
  } catch (_){ texteCopie = null; }

  // 2. Puis le menu à jour depuis le serveur, en arrière-plan.
  //    cache: 'no-store' → jamais servi depuis le cache du navigateur ;
  //    le réseau de GitHub Pages peut garder une version jusqu'à dix minutes.
  try {
    const texte = window.menuEnCours
      ? await window.menuEnCours                       // téléchargement lancé dans l'en-tête de la page
      : await fetch(SOURCE, { cache: 'no-store' }).then(r => r.ok ? r.text() : Promise.reject(new Error(`HTTP ${r.status}`)));
    const frais = JSON.parse(texte);
    if (!menuValide(frais)) throw new Error('menu.json ne contient aucune carte');
    try { localStorage.setItem(CACHE_KEY, texte); } catch (_){ /* mode privé */ }
    if (texte !== texteCopie) afficher(frais, false);
  } catch (err){
    if (texteCopie){
      // Réseau absent ou instable : la copie locale reste affichée, on le signale.
      afficherPiedDePage(true);
      console.warn('Menu affiché hors connexion :', err.message);
    } else {
      document.getElementById('menu').innerHTML = `
        <p class="empty"><strong>Le menu n'a pas pu être chargé.</strong>
        Vérifiez votre connexion et rechargez la page.</p>`;
      console.error('Chargement du menu impossible :', err);
    }
  }
})();

/* Les fichiers de la page (polices, logo, styles, script) sont gardés en réserve
   sur le téléphone : aux visites suivantes, la page s'ouvre sans attendre le réseau. */
if ('serviceWorker' in navigator){
  navigator.serviceWorker.register('sw.js').catch(() => { /* facultatif */ });
}
