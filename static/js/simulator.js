const slider = document.getElementById('crisis-slider');
const sliderVal = document.getElementById('slider-val');
const survivalBar = document.getElementById('survival-bar');
const survivalText = document.getElementById('stat-survival');
const impactedText = document.getElementById('stat-impacted');
const criticalText = document.getElementById('stat-critical');
const refugesText = document.getElementById('stat-refuges');
const refugeCapText = document.getElementById('stat-refuge-cap');

slider.addEventListener('input', (e) => {
    const val = e.target.value;
    sliderVal.innerText = `${val}m`;
    
    // Alerte visuelle si le niveau dépasse 5m
    if(val > 5) {
        document.getElementById('controls').classList.add('critical-alert');
    } else {
        document.getElementById('controls').classList.remove('critical-alert');
    }

    // Appel au Backend
    triggerSimulation(val);
});

async function triggerSimulation(level) {
    try {
        // ✅ Correction : On utilise 'level' pour correspondre à ton app.py
        const response = await fetch(`/api/simulate?level=${level}`);
        const data = await response.json();
        
        // MISE À JOUR DE L'INTERFACE (UI)
        // data.stats.pct contient déjà la string "XX%" calculée par le Python
        survivalText.innerText = data.stats.pct;
        survivalBar.style.width = data.stats.pct;
        impactedText.innerText = `${data.stats.impactes} Bâtiments en danger`;
        
        // ✅ NOUVELLES STATS : Criticité + Refuges
        criticalText.innerText = data.stats.critical_count || 0;
        refugesText.innerText = data.stats.refuges_available || 0;
        refugeCapText.innerText = `${data.stats.refuge_capacity || 0} places`;

        // MISE À JOUR DE LA CARTE (Fonction dans map.js)
        if (typeof updateMapPoints === "function") {
            updateMapPoints(data.points);
        }
    } catch (error) {
        console.error("Erreur Simulation:", error);
    }
}

// Lancement initial à 0m
triggerSimulation(0);