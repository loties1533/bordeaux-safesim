const map = L.map('map', { 
    zoomControl: false,
    attributionControl: false,
    renderer: L.canvas()
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
        // ✅ Clés corrigées
        const color  = p.s === 'ok' ? '#10b981' : '#ef4444';
        const radius = p.s === 'ok' ? 5 : 8;

        // ✅ Utiliser p.n comme identifiant unique
        if (markersStore.has(p.n)) {
            const marker = markersStore.get(p.n);
            marker.setStyle({ 
                fillColor: color, 
                color: p.s === 'danger' ? '#ffffff' : color, 
                weight: p.s === 'danger' ? 2 : 1,
                radius: radius 
            });
        } else {
            // ✅ p.lng au lieu de p.lon
            const marker = L.circleMarker([p.lat, p.lng], {
                radius: radius,
                fillColor: color,
                color: color,
                weight: 1,
                fillOpacity: 0.8
            }).bindPopup(`
                <div style="font-family: 'Share Tech Mono', monospace;">
                    <b style="color: ${color}">${p.n}</b><br>
                    TYPE: ${p.t}<br>
                    CAPACITÉ: ${p.c || 'Non renseignée'}
                </div>
            `);
            
            marker.addTo(map);
            markersStore.set(p.n, marker);
        }
    });
};

window.switchTheme = function(mode) {
    baseTile.setUrl(themes[mode]);
};

setTimeout(() => map.invalidateSize(), 100);

document.getElementById('theme-toggle').addEventListener('click', () => {
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    const nextTheme = isLight ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', nextTheme);
    window.switchTheme(nextTheme);
});