const map = L.map('map', { 
    zoomControl: false,
    attributionControl: false,
    renderer: L.canvas() // ⚡ Performance pour gérer les milliers de points ERP
}).setView([44.8377, -0.5792], 13);

const themes = {
    dark: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    light: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png'
};

let baseTile = L.tileLayer(themes.dark).addTo(map);

// Tracé de la Garonne pour l'effet visuel
const garonnePath = [[44.8105, -0.5480], [44.8256, -0.5594], [44.8378, -0.5654], [44.8450, -0.5630], [44.8566, -0.5534], [44.8770, -0.5460]];
const floodLayer = L.layerGroup().addTo(map);
let markersStore = new Map();

window.visualizeFlood = function(level) {
    floodLayer.clearLayers();
    if (level <= 0) return;
    L.polyline(garonnePath, { color: '#3b82f6', weight: level * 45, opacity: 0.35, lineCap: 'round', interactive: false }).addTo(floodLayer);
};

window.updateMapPoints = function(points) {
    points.forEach(p => {
        const color = p.status === 'ok' ? '#10b981' : '#ef4444';
        const radius = p.status === 'ok' ? 5 : 8;

        // Construction du Pop-up détaillé
        const popupContent = `
            <div style="font-family: 'Share Tech Mono', monospace; min-width: 180px;">
                <div style="border-bottom: 1px solid ${color}44; margin-bottom: 8px; padding-bottom: 4px;">
                    <b style="color: ${color}; text-transform: uppercase; font-size: 14px;">${p.nom}</b>
                </div>
                <div style="font-size: 11px; line-height: 1.5; color: #94a3b8;">
                    <div>TYPE: <span style="color: #f1f5f9;">${p.type}</span></div>
                    <div>CAPACITÉ: <span style="color: #f1f5f9;">${p.capacite} pers.</span></div>
                    <div>SEUIL CRITIQUE: <span style="color: #10b981;">${p.seuil_visuel}m</span></div>
                    <div style="margin-top: 8px; padding: 2px 6px; background: ${p.status === 'danger' ? '#450a0a' : '#064e3b'}; color: ${p.status === 'danger' ? '#fecaca' : '#d1fae5'}; text-align: center; font-weight: bold; font-size: 10px;">
                        ${p.status === 'danger' ? '⚠️ ZONE SUBMERGÉE' : '✅ OPÉRATIONNEL'}
                    </div>
                </div>
            </div>
        `;

        if (markersStore.has(p.id)) {
            const marker = markersStore.get(p.id);
            marker.setStyle({ 
                fillColor: color, 
                color: p.status === 'danger' ? '#fff' : color, 
                radius: radius 
            });
            // Mise à jour du contenu du pop-up (si l'utilisateur l'a ouvert)
            marker.setPopupContent(popupContent);
        } else {
            const marker = L.circleMarker([p.lat, p.lon], { 
                radius: radius, 
                fillColor: color, 
                color: color, 
                weight: 1, 
                fillOpacity: 0.8 
            }).bindPopup(popupContent);
            
            marker.addTo(map);
            markersStore.set(p.id, marker);
        }
    });
};

// Gestion du bouton Thème sécurisée
document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('theme-toggle');
    if(btn) {
        btn.addEventListener('click', () => {
            const isLight = document.documentElement.getAttribute('data-theme') === 'light';
            const next = isLight ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', next);
            baseTile.setUrl(themes[next]);
        });
    }
});