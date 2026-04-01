const slider = document.getElementById('crisis-slider');
const sliderVal = document.getElementById('slider-val');
const survivalBar = document.getElementById('survival-bar');
const survivalText = document.getElementById('stat-survival');
const impactedText = document.getElementById('stat-impacted');

slider.addEventListener('input', (e) => {
    const val = e.target.value;
    sliderVal.innerText = `${val}m`;
    
    // Si niveau élevé, on change le look
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
        const response = await fetch(`/api/simulate?niveau=${level}`);
        const data = await response.json();
        
        // Update UI
        survivalText.innerText = `${100 - data.stats.pct}%`;
        survivalBar.style.width = `${100 - data.stats.pct}%`;
        impactedText.innerText = `${data.stats.impactes} Impactés`;

        // Update Map (Fonction du Dev 3)
        if (typeof updateMapPoints === "function") {
            updateMapPoints(data.points);
        }
    } catch (error) {
        console.error("Erreur Simulation:", error);
    }
}
triggerSimulation(0);