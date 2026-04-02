import os
import hashlib
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
    niveau = float(request.args.get('niveau', 2.0))
    df_erp = load_clean_data()
    
    if df_erp.empty:
        return jsonify({"statistiques": {"total_impacte": 0, "pourcentage_impact": "0%"}, "points": []})

    # --- LE FIX STATISTIQUE ---
    # 1. On définit la population réelle de Bordeaux (chiffre INSEE)
    POPULATION_BORDEAUX = 260000 
    
    # 2. On calcule la capacité cumulée de TOUS les ERP du fichier
    capacite_cumulee_totale = df_erp['capacite'].sum()
    
    # 3. On crée un ratio : 1 place en ERP représente X habitant réel
    # Cela permet de ramener tes 2 millions à 260 000
    ratio_habitant = POPULATION_BORDEAUX / capacite_cumulee_totale if capacite_cumulee_totale > 0 else 0
    # --------------------------

    total_capacite_impactee = 0
    points = []

    # On filtre pour l'affichage (points importants)
    mask = (df_erp['type'].isin(TYPES_CRITIQUES)) | (df_erp['capacite'] > 20)
    df_display = df_erp[mask]

    for i, row in df_display.iterrows():
        alt = row['altitude']
        is_flooded = niveau >= alt
        status = "danger" if is_flooded else "ok"
        
        if is_flooded:
            total_capacite_impactee += row['capacite']
            
        points.append({
            "id": str(i), "lat": row['lat'], "lon": row['lng'],
            "nom": row['nom'], "status": status,
            "capacite": int(row['capacite']), "type": row['type'],
            "alt": alt
        })

    # Calcul final pondéré
    habitants_impactes = int(total_capacite_impactee * ratio_habitant)
    pourcentage_impact = (habitants_impactes / POPULATION_BORDEAUX) * 100

    return jsonify({
        "statistiques": {
            "total_impacte": habitants_impactes,
            "pourcentage_impact": f"{round(pourcentage_impact, 1)}%"
        },
        "points": points
    })

if __name__ == '__main__':
    # Mode debug actif pour le développement
    app.run(debug=True, port=5000)