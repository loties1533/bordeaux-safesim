const slider = document.getElementById('crisis-slider');
const sliderVal = document.getElementById('slider-val');
const statSurvival = document.getElementById('stat-survival');
const statImpacted = document.getElementById('stat-impacted');
const survivalBar = document.getElementById('survival-bar');

function updateSimulation() {
    const level = slider.value;
    sliderVal.innerText = `${parseFloat(level).toFixed(1)}m`;

    fetch(`/api/simulate?niveau=${level}`)
        .then(res => res.json())
        .then(data => {
            // On affiche le taux d'impact envoyé par app.py
            statSurvival.innerText = data.statistiques.pourcentage_impact;
            statImpacted.innerText = `${data.statistiques.total_impacte.toLocaleString()} habitants impactés`;

            // Remplissage de la barre
            survivalBar.style.width = data.statistiques.pourcentage_impact;
            
            // Changement de couleur dynamique
            const percent = parseFloat(data.statistiques.pourcentage_impact);
            if (percent > 50) {
                survivalBar.className = "bg-red-600 h-full transition-all duration-500";
            } else if (percent > 20) {
                survivalBar.className = "bg-orange-500 h-full transition-all duration-500";
            } else {
                survivalBar.className = "bg-emerald-500 h-full transition-all duration-500";
            }

            if (window.updateMapPoints) window.updateMapPoints(data.points);
        });
}

let debounceTimer = null;
slider.addEventListener('input', () => {
    sliderVal.innerText = `${parseFloat(slider.value).toFixed(1)}m`;
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(updateSimulation, 120);
});
updateSimulation();