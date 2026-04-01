from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
import hashlib

app = Flask(__name__)

# Configuration des chemins
DATA_PATH = 'data/bor_erp_managed.csv'

# Types d'ERP prioritaires pour la gestion de crise
TYPES_CRITIQUES = [
    'Hôpitaux / cliniques', 
    'Maisons de retraite / handicapés', 
    'Mairies / administrations', 
    'Écoles / collèges / lycées'
]

def load_data():
    if os.path.exists(DATA_PATH):
        # Lecture avec le délimiteur "|" utilisé par ton collègue
        return pd.read_csv(DATA_PATH, sep="|")
    return pd.DataFrame()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/simulate')
def simulate():
    niveau = float(request.args.get('niveau', 0))
    df_erp = load_data()
    
    if df_erp.empty:
        return jsonify({"statistiques": {"total_impacte": 0, "pourcentage_survie": "100%"}, "points": []})

    points = []
    total_impacte = 0
    
    # Filtrage pour la clarté visuelle
    # On garde : les types critiques OU les bâtiments avec capacité > 20
    mask = (df_erp['type'].isin(TYPES_CRITIQUES)) | (df_erp['capacite'] > 20)
    df_filtered = df_erp[mask]
    
    # Capacité totale basée sur le fichier complet pour la précision statistique
    total_capacite_ville = df_erp['capacite'].sum()

    for i, row in df_filtered.iterrows():
        # Ajout d'un "bruit" visuel pour éviter l'effet de bloc par quartier (décalage entre 0 et 0.5m)
        offset = (int(hashlib.md5(row['nom'].encode()).hexdigest(), 16) % 50) / 100
        seuil_ajuste = row['seuil'] + offset
        
        status = "danger" if niveau >= seuil_ajuste else "ok"
        
        if status == "danger":
            total_impacte += row['capacite']
            
        points.append({
            "id": str(i),
            "lat": row['lat'],
            "lon": row['lng'],
            "nom": row['nom'],
            "status": status,
            "capacite": int(row['capacite']),
            "type": row['type'],
            "seuil_visuel": row['seuil'] # Ajouté pour l'affichage dans le pop-up JS
        })

    # Calcul du taux de survie global
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