// --- CONFIGURATION DE LA CARTE ---
// On garde un fond de carte clair et élégant (Voyager) qui va bien avec l'émeraude
const map = L.map('map', { 
    zoomControl: false,
    attributionControl: false,
    renderer: L.canvas() // Plus performant pour afficher beaucoup de points
}).setView([44.8377, -0.5792], 13);

// Ajout du fond de carte unique
L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png').addTo(map);

// Déplacement du zoom en bas à droite pour libérer de la place pour le bouton Retour
L.control.zoom({ position: 'bottomright' }).addTo(map);

// Stockage des points pour éviter de recréer les objets à chaque mouvement du slider
let markersStore = new Map();

// --- LOGIQUE DES POINTS (CRUES) ---
window.updateMapPoints = function(points) {
    points.forEach(p => {
        const isDanger = p.status === 'danger';
        const color = isDanger ? '#ef4444' : '#10b981'; // Rouge vs Émeraude
        const radius = isDanger ? 8 : 5;

        // Préparation des lignes d'info
        const floodInfo = p.flood_req 
            ? `<div style="background: #fff7ed; padding: 4px; border-radius: 4px; border: 1px solid #ffedd5; margin-top: 5px;">
                 <span style="font-size: 9px; color: #9a3412; font-weight: bold; text-transform: uppercase;">Seuil de submersion</span><br>
                 <b style="color: #c2410c;">&ge; ${p.flood_req}m NGF</b>
               </div>`
            : `<div style="color: #94a3b8; font-size: 10px; margin-top: 5px; font-style: italic;">Hors zone d'atteinte fleuve</div>`;

        const popupContent = `
            <div style="font-family: 'Inter', sans-serif; min-width: 200px; padding: 5px;">
                <div style="text-transform: uppercase; font-size: 10px; font-weight: 800; color: #64748b; letter-spacing: 0.05em;">${p.type}</div>
                <b style="color: #1e293b; font-size: 15px; display: block; margin-bottom: 8px;">${p.nom}</b>
                
                <div style="font-size: 12px; color: #475569; display: flex; flex-direction: column; gap: 4px;">
                    <div>Capacité : <b>${p.capacite} places</b></div>
                    <div>Altitude sol : <b>${p.alt}m</b></div>
                    ${floodInfo}
                </div>

                <div style="margin-top: 12px; padding: 6px; border-radius: 6px; background: ${isDanger ? '#fef2f2' : '#f0fdf4'}; 
                            color: ${isDanger ? '#b91c1c' : '#15803d'}; text-align: center; font-weight: 600; font-size: 11px; border: 1px solid ${isDanger ? '#fecaca' : '#bbf7d0'};">
                    ${isDanger ? '⚠️ ÉTABLISSEMENT SUBMERGÉ' : '✅ SITE OPÉRATIONNEL'}
                </div>
            </div>`;

        if (markersStore.has(p.id)) {
            const marker = markersStore.get(p.id);
            marker.setStyle({ fillColor: color, color: isDanger ? '#fff' : color, radius: radius, weight: isDanger ? 2 : 1 });
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

// --- SECURITÉ POUR LES AUTRES PAGES ---
// On vérifie si l'élément theme-toggle existe avant d'ajouter l'écouteur
// Cela évite de faire planter le JS sur la page Heatmap où le bouton n'existe pas
const themeToggle = document.getElementById('theme-toggle');
if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        console.log("Le mode sombre a été désactivé par l'administrateur.");
    });
}