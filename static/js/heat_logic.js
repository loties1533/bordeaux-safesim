document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialisation de la carte SANS le zoom par défaut
    const map = L.map('map', {
        zoomControl: false // On désactive le zoom natif en haut à gauche
    }).setView([44.837789, -0.57918], 12);

    // Ajout du contrôle de zoom en bas à droite (pour correspondre au CSS Glassmorphism)
    L.control.zoom({
        position: 'bottomright'
    }).addTo(map);

    // 2. Fond de carte clair pour bien faire ressortir les couleurs
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        maxZoom: 19
    }).addTo(map);

    console.log("Chargement des données thermiques en cours...");

    // 3. Récupération du fichier
    fetch('/static/data/ri_icu_ifu_s.geojson')
        .then(response => response.json())
        .then(data => {
            L.geoJSON(data, {
                renderer: L.canvas({ padding: 0.5 }), 
                
                style: function(feature) {
                    // LE SECRET EST LÀ : On utilise le "delta" de température !
                    const delta = feature.properties.delta || 0;
                    
                    // Si le delta est supérieur à 0, c'est qu'il fait plus chaud (Chaleur)
                    // Sinon, c'est qu'il fait plus frais (Fraîcheur)
                    const isHeat = delta > 0;

                    return {
                        fillColor: isHeat ? '#fb923c' : '#38bdf8', // Orange si > 0, Bleu si < 0
                        color: isHeat ? '#ea580c' : '#0284c7',
                        weight: 1,
                        fillOpacity: 0.6,
                        opacity: 0.8
                    };
                }
            }).addTo(map);
            
            console.log("Boom ! Couleurs appliquées avec succès grâce au delta !");
        })
        .catch(error => console.error("Erreur lors du chargement :", error));
});