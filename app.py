import os
import pandas as pd
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# --- CONFIGURATION ---
DATA_PATH = os.path.join('data', 'bor_erp_managed.csv')

# Liste des ERP prioritaires pour l'affichage et la gestion de crise
TYPES_CRITIQUES = [
    'Hôpitaux / cliniques', 
    'Maisons de retraite / handicapés', 
    'Mairies / administrations', 
    'Écoles / collèges / lycées'
]

# --- LOGIQUE DE DONNÉES ---

def load_clean_data():
    """Charge le CSV et nettoie les erreurs d'altimétrie."""
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()
    
    df = pd.read_csv(DATA_PATH, sep="|")
    
    # On ignore les points où l'altitude a échoué (-9999) 
    # pour ne pas fausser les stats ou la carte
    if not df.empty and 'altitude' in df.columns:
        df = df[df['altitude'] > -100]
        
    return df

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/simulate')
def simulate():
    # 1. Récupération du niveau du slider (défaut 0.0)
    try:
        niveau = float(request.args.get('niveau', 0))
    except ValueError:
        niveau = 0.0

    # 2. Chargement des données
    df_erp = load_clean_data()
    
    if df_erp.empty:
        return jsonify({
            "statistiques": {"total_impacte": 0, "pourcentage_impact": "0%"},
            "points": []
        })

    # 3. Initialisation des compteurs
    points = []
    total_impacte = 0
    total_capacite_ville = df_erp['capacite'].sum()

    # 4. Filtrage pour la performance visuelle de la carte
    # On n'affiche que les ERP critiques OU ceux ayant une capacité > 20
    mask = (df_erp['type'].isin(TYPES_CRITIQUES)) | (df_erp['capacite'] > 20)
    df_display = df_erp[mask]

    # 5. Traitement des points
    for i, row in df_display.iterrows():
        flood_req = row.get('flood_level_req')
        reachable = pd.notna(flood_req)
        zone = row.get('zone_ppri')

        # Un ERP est submergé si le niveau de crue dépasse :
        # - le seuil de connectivité hydraulique (flood fill) : l'eau peut atteindre sa zone
        # - ET l'altitude réelle du bâtiment : l'eau a monté jusqu'à son rez-de-chaussée
        effective_threshold = max(float(flood_req), float(row['altitude'])) if reachable else None
        is_flooded = reachable and niveau >= effective_threshold
        status = "danger" if is_flooded else "ok"

        if is_flooded:
            total_impacte += row['capacite']

        points.append({
            "id": str(i),
            "lat": row['lat'],
            "lon": row['lng'],
            "nom": row['nom'],
            "status": status,
            "capacite": int(row['capacite']),
            "type": row['type'],
            "alt": row['altitude'],
            "flood_req": round(effective_threshold, 2) if reachable else None,
            "zone_ppri": zone if pd.notna(zone) and isinstance(zone, str) else None,
        })

    # 6. Calcul du taux d'impact global (0% -> 100%)
    impact_rate = (total_impacte / total_capacite_ville * 100) if total_capacite_ville > 0 else 0

    return jsonify({
        "statistiques": {
            "total_impacte": int(total_impacte),
            "pourcentage_impact": f"{round(impact_rate, 1)}%"
        },
        "points": points
    })

if __name__ == '__main__':
    # Mode debug actif pour le développement
    app.run(debug=True, port=5000)
