const themes = {
    light: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
    dark: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
};

const map = L.map('map', { 
    zoomControl: false,
    attributionControl: false,
    renderer: L.canvas() 
}).setView([44.8377, -0.5792], 13);

// Mode clair par défaut
let baseTile = L.tileLayer(themes.light).addTo(map);
document.documentElement.setAttribute('data-theme', 'light');

let markersStore = new Map();

window.updateMapPoints = function(points) {
    points.forEach(p => {
        const color = p.status === 'ok' ? '#10b981' : '#ef4444';
        const radius = p.status === 'ok' ? 5 : 8;

        const popupContent = `
            <div style="font-family: 'Share Tech Mono', monospace; min-width: 180px; color: #1e293b;">
                <b style="color: ${color}; text-transform: uppercase; font-size: 14px;">${p.nom}</b>
                <div style="margin-top: 5px; font-size: 12px; line-height: 1.4;">
                    <div>TYPE: <b>${p.type}</b></div>
                    <div>CAPACITÉ: <b>${p.capacite} pers.</b></div>
                    <div style="background: #f1f5f9; padding: 2px 4px; margin-top: 4px;">
                        ALTITUDE: <b style="color: #166534;">${p.alt}m NGF</b>
                    </div>
                </div>
                <div style="margin-top: 8px; padding: 4px; background: ${p.status === 'danger' ? '#fee2e2' : '#d1fae5'}; color: ${p.status === 'danger' ? '#991b1b' : '#065f46'}; text-align: center; font-weight: bold; font-size: 11px;">
                    ${p.status === 'danger' ? '⚠️ SUBMERGÉ' : '✅ OPÉRATIONNEL'}
                </div>
            </div>`;

        if (markersStore.has(p.id)) {
            const marker = markersStore.get(p.id);
            marker.setStyle({ fillColor: color, color: p.status === 'danger' ? '#fff' : color, radius: radius });
            marker.setPopupContent(popupContent);
        } else {
            const marker = L.circleMarker([p.lat, p.lon], { radius: radius, fillColor: color, color: color, weight: 1, fillOpacity: 0.8 }).bindPopup(popupContent);
            marker.addTo(map);
            markersStore.set(p.id, marker);
        }
    });
};

document.getElementById('theme-toggle').addEventListener('click', () => {
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    const nextTheme = isLight ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', nextTheme);
    
    baseTile.setUrl(themes[nextTheme]);
});