/* Service worker du menu KING FOOD.
   Garde en réserve les fichiers de la page (polices, logo, styles, script) pour un
   affichage immédiat aux visites suivantes, même avec un réseau lent ou absent.
   Chaque fichier servi depuis la réserve est aussi redemandé en arrière-plan et
   remplacé s'il a changé : une mise à jour de la page apparaît à la visite d'après.
   menu.json n'est jamais mis en réserve ici : la page le charge elle-même. */
const RESERVE = 'kingfood-page-v1';
const FICHIERS = [
  './', 'index.html', 'carte.css', 'identite.css', 'carte.js', 'logo.png', 'favicon.png',
  'polices/polices.css', 'polices/montserrat-400.woff2', 'polices/montserrat-700.woff2', 'polices/montserrat-800.woff2'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(RESERVE).then(c => c.addAll(FICHIERS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(cles => Promise.all(cles.filter(k => k !== RESERVE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== self.location.origin) return;
  if (url.pathname.endsWith('/menu.json')) return;   // toujours le réseau, géré par la page
  e.respondWith(caches.open(RESERVE).then(async reserve => {
    const enReserve = await reserve.match(e.request);
    const depuisReseau = fetch(e.request)
      .then(rep => { if (rep.ok) reserve.put(e.request, rep.clone()); return rep; })
      .catch(() => null);
    e.waitUntil(depuisReseau);
    return enReserve || (await depuisReseau) || Response.error();
  }));
});
