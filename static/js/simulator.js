const slider = document.getElementById('crisis-slider');
const sliderVal = document.getElementById('slider-val');
const statSurvival = document.getElementById('stat-survival');
const statImpacted = document.getElementById('stat-impacted');
const survivalBar = document.getElementById('survival-bar');

// NOUVEAUX ÉLÉMENTS (Assure-toi que les ID existent dans ton index.html)
const transportStatus = document.getElementById('transport-status');
const lignesList = document.getElementById('lignes-hs-list');
const lieuxCount = document.getElementById('lieux-count');
const lieuxList = document.getElementById('lieux-list');

function updateSimulation() {
    const level = slider.value;
    sliderVal.innerText = `${parseFloat(level).toFixed(2)}m`;

    fetch(`/api/simulate?niveau=${level}`)
        .then(res => res.json())
        .then(data => {
            // --- 1. POPULATION (Ton code existant) ---
            statSurvival.innerText = data.statistiques.pourcentage_impact;
            statImpacted.innerText = `${data.statistiques.total_impacte.toLocaleString()} habitants impactés`;
            survivalBar.style.width = data.statistiques.pourcentage_impact;
            
            const percent = parseFloat(data.statistiques.pourcentage_impact);
            if (percent > 50) {
                survivalBar.className = "bg-red-600 h-full transition-all duration-500";
            } else if (percent > 20) {
                survivalBar.className = "bg-orange-500 h-full transition-all duration-500";
            } else {
                survivalBar.className = "bg-emerald-500 h-full transition-all duration-500";
            }

            // --- 2. TRANSPORT (Nouveauté) ---
            if (transportStatus && lignesList) {
                transportStatus.innerText = data.transport.status;
                
                if (data.transport.status === "ALERTE") {
                    transportStatus.className = "text-2xl font-bold text-red-500"; // Tailwind
                    // On affiche les lignes impactées
                    lignesList.innerHTML = `<strong>Lignes coupées :</strong> ${data.transport.lignes_touchees.join(', ')}`;
                } else {
                    transportStatus.className = "text-2xl font-bold text-emerald-500";
                    lignesList.innerHTML = "Trafic normal sur le réseau TBM";
                }
            }

            // --- 3. ACCESSIBILITÉ (Nouveauté) ---
            if (lieuxCount && lieuxList) {
                lieuxCount.innerText = data.statistiques.nb_lieux_isoles;
                
                if (data.statistiques.nb_lieux_isoles > 0) {
                    lieuxCount.className = "text-2xl font-bold text-red-600";
                    // On affiche les noms des établissements isolés
                    lieuxList.innerHTML = `<strong>Établissements isolés :</strong><br>${data.transport.lieux_isoles.join('<br>')}`;
                } else {
                    lieuxCount.className = "text-2xl font-bold text-gray-400";
                    lieuxList.innerHTML = "Tous les établissements sont accessibles";
                }
            }

            // --- 4. CARTE ---
            if (window.updateMapPoints) window.updateMapPoints(data.points);
        })
        .catch(err => console.error("Erreur Fetch:", err));
}

slider.addEventListener('input', updateSimulation);
updateSimulation();