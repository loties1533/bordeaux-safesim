// 1. Initialisation avec un fond de carte sombre
const map = L.map('map', { 
    zoomControl: false,
    attributionControl: false // Optionnel : pour épurer le look War Room
}).setView([44.8377, -0.5792], 13);

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: 'Bordeaux Metropole | DataVisualisation'
}).addTo(map);

// 2. Groupe de points pour un rafraîchissement rapide
let erpLayer = L.layerGroup().addTo(map);

// 3. LA FONCTION DE RENDU (Corrigée pour le Chef d'Orchestre)
window.updateMapPoints = function(points) {
    // On vide les anciens points avant de dessiner les nouveaux
    erpLayer.clearLayers();
    
    if (!points || points.length === 0) return;

    points.forEach(p => {
        // Couleurs néon : Vert si OK, Rouge si Danger
        const color = p.status === 'ok' ? '#10b981' : '#ef4444';
        
        const marker = L.circleMarker([p.lat, p.lon], {
            radius: 5,
            fillColor: color,
            color: color,
            weight: 1,
            fillOpacity: 0.8
        }).bindPopup(`
            <div style="font-family: 'Share Tech Mono', monospace;">
                <b style="color: ${color}">${p.nom}</b><br>
                STATUS: ${p.status.toUpperCase()}<br>
                CAPACITÉ: ${p.capacite}
            </div>
        `);
        
        erpLayer.addLayer(marker);
    });
};

// Petit fix : s'assurer que la carte se redimensionne bien au chargement
setTimeout(() => {
    map.invalidateSize();
}, 100);