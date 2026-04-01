/**
 * bordeaux-safesim/static/js/map.js
 * MAJ : Intégration Dev 3 dans le design du Dev 4
 */

// 1. Initialisation avec Rendu CANVAS (Indispensable pour 8000+ points)
const map = L.map('map', { 
    zoomControl: false,
    attributionControl: false,
    renderer: L.canvas() // ⚡ TA TOUCHE EXPERT : Performance maximale
}).setView([44.8377, -0.5792], 13);

// Fonds de carte (Prêt pour le switch de thème)
const themes = {
    dark: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    light: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png'
};

let baseTile = L.tileLayer(themes.dark).addTo(map);

// 2. Gestion intelligente des marqueurs (On ne vide pas tout, on met à jour)
let markersStore = new Map(); // On stocke les objets Leaflet ici

window.updateMapPoints = function(points) {
    if (!points) return;

    points.forEach(p => {
        // Définition du style selon le statut 
        const color = p.status === 'ok' ? '#10b981' : '#ef4444';
        const radius = p.status === 'ok' ? 5 : 8;

        if (markersStore.has(p.id)) {
            // MISE À JOUR DU POINT EXISTANT 
            const marker = markersStore.get(p.id);
            marker.setStyle({ 
                fillColor: color, 
                color: p.status === 'danger' ? '#ffffff' : color, 
                weight: p.status === 'danger' ? 2 : 1,
                radius: radius 
            });
        } else {
            // CRÉATION INITIALE (si le point n'existe pas encore sur la carte) 
            const marker = L.circleMarker([p.lat, p.lon], {
                radius: radius,
                fillColor: color,
                color: color,
                weight: 1,
                fillOpacity: 0.8
            }).bindPopup(`
                <div style="font-family: 'Share Tech Mono', monospace; color: #10b981;">
                    <b style="color: ${color}">${p.nom}</b><br>
                    CAPACITÉ: ${p.capacite || 'Non renseignée'}
                </div>
            `);
            
            marker.addTo(map);
            markersStore.set(p.id, marker);
        }
    });
};

// 3. LA MÉTHODE POUR CHANGER DE THÈME (À proposer au Dev 4)
window.switchTheme = function(mode) {
    baseTile.setUrl(themes[mode]);
};

// Fix affichage
setTimeout(() => map.invalidateSize(), 100);

document.getElementById('theme-toggle').addEventListener('click', () => {
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    const nextTheme = isLight ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', nextTheme);
    window.switchTheme(nextTheme); // Appelle ta fonction de swap de tiles
});