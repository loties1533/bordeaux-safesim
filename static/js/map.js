const map = L.map('map', { 
    zoomControl: false,
    attributionControl: false,
    renderer: L.canvas() // Plus performant pour des milliers de points
}).setView([44.8377, -0.5792], 13);

const themes = {
    dark: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    light: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png'
};

let baseTile = L.tileLayer(themes.dark).addTo(map);
let markersStore = new Map();

window.updateMapPoints = function(points) {
    if (!points) return;

    points.forEach(p => {
        // ✅ Synchronisation avec les clés de ton app.py (p.s pour status)
        const isDanger = (p.s === 'danger');
        const color    = isDanger ? '#ef4444' : '#10b981';
        const radius   = isDanger ? 8 : 5;

        // Si le point existe déjà, on change juste son look (plus rapide)
        if (markersStore.has(p.n)) {
            const marker = markersStore.get(p.n);
            marker.setStyle({ 
                fillColor: color, 
                color: isDanger ? '#ffffff' : color, 
                weight: isDanger ? 2 : 1,
                radius: radius 
            });
        } else {
            // Création du point s'il n'existe pas encore
            const marker = L.circleMarker([p.lat, p.lng], {
                radius: radius,
                fillColor: color,
                color: color,
                weight: 1,
                fillOpacity: 0.8
            }).bindPopup(`
                <div style="font-family: 'Share Tech Mono', monospace; min-width:150px;">
                    <b style="color: ${color}; font-size:1.1em;">${p.n}</b><br>
                    <hr style="border:0; border-top:1px solid #444; margin:5px 0;">
                    TYPE: ${p.t}<br>
                    CAPACITÉ: ${p.c || 'Non renseignée'}<br>
                    STATUT: ${isDanger ? '⚠️ INONDÉ' : '✅ SEC'}
                </div>
            `);
            
            marker.addTo(map);
            markersStore.set(p.n, marker);
        }
    });
};

// Gestion du changement de thème (Jour/Nuit)
window.switchTheme = function(mode) {
    baseTile.setUrl(themes[mode]);
};

// Correction bug d'affichage Leaflet au chargement
setTimeout(() => map.invalidateSize(), 100);

document.getElementById('theme-toggle').addEventListener('click', () => {
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    const nextTheme = isLight ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', nextTheme);
    window.switchTheme(nextTheme);
});