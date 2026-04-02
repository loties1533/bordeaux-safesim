from flask import Flask, render_template, jsonify, request
import pandas as pd
import os

app = Flask(__name__)

DATA_PATH = 'data/bor_erp_managed.csv'

TYPES_CRITIQUES = [
    'Hôpitaux / cliniques',
    'Maisons de retraite / handicapés',
    'Mairies / administrations',
    'Écoles / collèges / lycées'
]

CRITICAL_LEVELS = {
    'Hôpitaux / cliniques': 9,
    'Maisons de retraite / handicapés': 8,
    'Écoles / collèges / lycées': 7,
    'Gymnases / sports couverts': 6,
    'Mairies / administrations': 5,
    'Salles de spectacle / conférences': 4,
    'Hôtels / hébergements': 3,
    'Centres commerciaux': 2,
    'Bibliothèques / médiathèques': 1,
    "Halls d'exposition": 0,
}

REFUGE_TYPES = ['Gymnases / sports couverts', 'Écoles / collèges / lycées', 'Mairies / administrations']
REFUGE_SEUIL_MIN = 6


def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH, sep="|")
    return pd.DataFrame()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/simulate')
def simulate():
    niveau = float(request.args.get('level', request.args.get('niveau', 0)))
    df_erp = load_data()

    if df_erp.empty:
        return jsonify({"stats": {"impactes": 0, "pct": "100%"}, "points": []})

    points = []
    total_impacte       = 0
    critical_count      = 0
    refuges_active      = []

    # Filtrage visuel : critiques OU capacité > 20
    mask        = (df_erp['type'].isin(TYPES_CRITIQUES)) | (df_erp['capacite'] > 20)
    df_filtered = df_erp[mask]

    # Capacité totale pour le calcul de survie
    total_capacite_ville = df_erp['capacite'].sum()

    for i, row in df_filtered.iterrows():
        status = "danger" if niveau >= row['seuil'] else "ok"

        if status == "danger":
            total_impacte += row['capacite']
            # ── AJOUT : compteur critiques (hôpitaux + maisons retraite)
            if CRITICAL_LEVELS.get(row['type'], 0) >= 8:
                critical_count += 1
        else:
            # ── AJOUT : refuges disponibles
            if row['type'] in REFUGE_TYPES and row['seuil'] >= REFUGE_SEUIL_MIN:
                refuges_active.append(int(row['capacite']))

        points.append({
            "id":           str(i),
            "lat":          row['lat'],
            "lon":          row['lng'],
            "nom":          row['nom'],
            "status":       status,
            "capacite":     int(row['capacite']),
            "type":         row['type'],
            "seuil_visuel": row['seuil'],
        })

    survie = max(0, 100 - (total_impacte / total_capacite_ville * 100))

    return jsonify({
        "stats": {
            "impactes":          int(total_impacte),
            "pct":               f"{round(survie, 1)}%",
            # ── AJOUT : nouvelles stats pour le dashboard
            "critical_count":    critical_count,
            "refuges_available": len(refuges_active),
            "refuge_capacity":   sum(refuges_active),
        },
        "points": points,
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)