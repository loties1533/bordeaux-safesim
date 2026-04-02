import os
import pandas as pd
from flask import Flask, render_template, jsonify, request, send_from_directory

app = Flask(__name__)

# --- CONFIGURATION ---
DATA_PATH = os.path.join('data', 'bor_erp_managed.csv')

TYPES_CRITIQUES = [
    'Hôpitaux / cliniques',
    'Maisons de retraite / handicapés',
    'Mairies / administrations',
    'Écoles / collèges / lycées'
]

# --- CHARGEMENT UNIQUE AU DÉMARRAGE ---

def _load():
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame(), pd.DataFrame()
    df = pd.read_csv(DATA_PATH, sep="|")
    df = df[df['altitude'] > -100].copy()
    # Seuil effectif précalculé une seule fois
    df['effective_threshold'] = df[['flood_level_req', 'altitude']].max(axis=1)
    # Sous-ensemble affiché sur la carte
    mask = df['type'].isin(TYPES_CRITIQUES) | (df['capacite'] > 20)
    return df, df[mask].reset_index(drop=True)

DF_ALL, DF_DISPLAY = _load()

# --- ROUTES ---

@app.route('/')
def home():
    """Page d'accueil de présentation du projet Safe-City."""
    return render_template('home.html')

@app.route('/simulation')
def simulation():
    """Page du simulateur de crue (War Room)."""
    return render_template('index.html')

@app.route('/heat-map')
def heat_map():
    """Page des îlots de chaleur/fraîcheur."""
    return render_template('heat.html')

@app.route('/api/thermique')
def api_thermique():
    """Sert le fichier GeoJSON directement depuis le dossier data racine"""
    return send_from_directory('data', 'ri_icu_ifu_s.geojson')

# --- API DE SIMULATION ---

@app.route('/api/simulate')
def simulate():
    # 1. Récupération du niveau du slider (défaut 0.0)
    try:
        niveau = float(request.args.get('niveau', 0))
    except ValueError:
        niveau = 0.0

    if DF_ALL.empty:
        return jsonify({"statistiques": {"total_impacte": 0, "pourcentage_impact": "0%"}, "points": []})

    # Calcul vectorisé : masque de submersion
    flooded_mask = DF_DISPLAY['effective_threshold'] <= niveau

    # Stats sur tous les ERP (pas seulement ceux affichés)
    total_capacite_ville = DF_ALL['capacite'].sum()
    total_impacte = int(DF_ALL.loc[DF_ALL['effective_threshold'] <= niveau, 'capacite'].sum())
    impact_rate = (total_impacte / total_capacite_ville * 100) if total_capacite_ville > 0 else 0

    # Construction de la liste de points
    df = DF_DISPLAY.copy()
    df['status'] = flooded_mask.map({True: 'danger', False: 'ok'})
    df['flood_req_out'] = df['effective_threshold'].round(2)
    df['zone_ppri_out'] = df['zone_ppri'].where(df['zone_ppri'].notna() & df['zone_ppri'].apply(lambda x: isinstance(x, str)), other=None)

    points = df[['lat', 'lng', 'nom', 'status', 'capacite', 'type', 'altitude', 'flood_req_out', 'zone_ppri_out']].rename(
        columns={'lng': 'lon', 'altitude': 'alt', 'flood_req_out': 'flood_req', 'zone_ppri_out': 'zone_ppri'}
    ).assign(id=df.index.astype(str)).to_dict(orient='records')

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