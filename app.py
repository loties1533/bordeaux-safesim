from flask import Flask, render_template, jsonify, request
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Chemin vers le futur fichier de ton pote
DATA_PATH = 'data/processed/erp_managed.csv' # ou .json

def load_data():
    if os.path.exists(DATA_PATH):
        # Si ton pote fait un CSV :
        return pd.read_csv(DATA_PATH)
        # Si ton pote fait un JSON, remplace par : return pd.read_json(DATA_PATH)
    else:
        # Tes données de test actuelles pour ne pas travailler dans le noir
        data = [
            {'id': 1, 'nom': 'TEST_ZONE_A', 'lat': 44.83, 'lon': -0.56, 'seuil_critique': 1.5, 'capacite': 100},
            {'id': 2, 'nom': 'TEST_ZONE_B', 'lat': 44.85, 'lon': -0.58, 'seuil_critique': 3.0, 'capacite': 200}
        ]
        return pd.DataFrame(data)

@app.route('/api/simulate')
def simulate():
    niveau = float(request.args.get('niveau', 0))
    df_erp = load_data() # On recharge les données
    
    points = []
    total_impacte = 0
    total_capacite_ville = df_erp['capacite'].sum() if not df_erp.empty else 1
    
    for _, row in df_erp.iterrows():
        status = "danger" if niveau >= row['seuil_critique'] else "ok"
        if status == "danger":
            total_impacte += row['capacite']
            
        points.append({
            "id": str(row['id']), # On force en string pour le markersStore du JS
            "lat": row['lat'],
            "lon": row['lon'],
            "nom": row['nom'],
            "status": status,
            "capacite": row['capacite']
        })

    # Calcul réel de survie basé sur la capacité totale
    survie = max(0, 100 - (total_impacte / total_capacite_ville * 100))

    return jsonify({
        "statistiques": {
            "total_impacte": int(total_impacte),
            "pourcentage_survie": f"{round(survie, 1)}%"
        },
        "points": points
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)