document.addEventListener('DOMContentLoaded', () => {
    if (typeof map === 'undefined') return;

    const turboRenderer = L.canvas({ padding: 0.5 });
    console.log("Appel de l'API Python pour les données thermiques...");

    // On appelle notre nouvelle route Flask !
    fetch('/api/thermique')
        .then(async res => {
            // Sécurité : si Flask renvoie une erreur, on l'affiche en clair au lieu de planter
            if (!res.ok) {
                const errText = await res.text();
                throw new Error(`Erreur serveur (${res.status}): ${errText}`);
            }
            return res.json();
        })
        .then(data => {
            L.geoJSON(data, {
                renderer: turboRenderer,
                style: function(feature) {
                    const dim = feature.properties.dimension;
                    const isHeat = (dim === 'ICU');

                    return {
                        fillColor: isHeat ? '#fb923c' : '#38bdf8',
                        color: isHeat ? '#ea580c' : '#0284c7',
                        weight: 0.5,
                        fillOpacity: 0.5,
                        opacity: 0.6
                    };
                },
                onEachFeature: function(feature, layer) {
                    layer.on('click', function() {
                        const isHeat = feature.properties.dimension === 'ICU';
                        const label = isHeat ? 'Îlot de Chaleur' : 'Zone de Fraîcheur';
                        const color = isHeat ? '#ea580c' : '#0369a1';
                        
                        layer.bindPopup(`
                            <div style="font-family: 'Inter', sans-serif;">
                                <strong style="color: ${color};">${label}</strong><br>
                                <span style="font-size: 11px; color: #64748b;">Surface : ${Math.round(feature.properties.st_area_sh)} m²</span>
                            </div>
                        `).openPopup();
                    });
                }
            }).addTo(map);
            
            console.log("SUCCÈS ! Carte thermique chargée via API Python.");
        })
        .catch(err => console.error("Échec du chargement :", err));
});