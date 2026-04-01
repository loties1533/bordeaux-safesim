from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
import csv  # Indispensable pour lire le fichier d'Axel

app = Flask(__name__)
CORS(app)

# ─── CONFIGURATION DES CHEMINS ───────────────────────────
# On cible le fichier généré par le script d'Axel
DATA_PATH = os.path.join('data', 'bor_erp_managed.csv')

FAKE_DATA = [
    {"nom": "MODE TEST : Gymnase Barbey", "lat": 44.8268, "lng": -0.5703, "seuil": 3, "capacite": 500},
    {"nom": "MODE TEST : École Achard", "lat": 44.8612, "lng": -0.5445, "seuil": 6, "capacite": 300}
]

# ─── CHARGEMENT DE LA DATA (CSV -> PYTHON) ───────────────
def load_database():
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                # Axel utilise le délimiteur "|" dans son script
                reader = csv.DictReader(f, delimiter="|")
                data = []
                for row in reader:
                    data.append({
                        "nom": row['nom'],
                        "lat": float(row['lat']),
                        "lng": float(row['lng']),
                        "type": row['type'],
                        "capacite": int(row['capacite']) if row['capacite'] else 0,
                        "seuil": int(row['seuil']) if row['seuil'] else 5
                    })
                print(f"✅ DATA RÉELLE CHARGÉE : {len(data)} établissements")
                return data
        except Exception as e:
            print(f"❌ Erreur lors de la lecture du CSV d'Axel : {e}")
            return FAKE_DATA
    else:
        print("⚠️ Fichier CSV introuvable dans /data. Passage en MODE TEST.")
        return FAKE_DATA

# On charge la base une seule fois au démarrage
DATABASE = load_database()

# ─── ROUTES ──────────────────────────────────────────────

@app.route('/')
def index():
    """Affiche l'interface War Room (le front d'Antoine/Orchestre)"""
    return render_template('index.html')

@app.route('/api/simulate', methods=['GET'])
def simulate():
    """Le moteur de simulation piloté par le slider"""
    # On récupère le niveau (0 à 10) envoyé par le slider
    val = request.args.get('level') or request.args.get('niveau') or 0
    level = float(val)

    results = []
    impactes_count = 0
    cap_perdue = 0

    for erp in DATABASE:
        # LOGIQUE DE CRISE : niveau d'eau >= seuil du bâtiment ?
        if level >= erp['seuil']:
            status = "danger"
            impactes_count += 1
            cap_perdue += erp['capacite']
        else:
            status = "ok"

        # On renvoie les clés simplifiées pour économiser de la bande passante
        # n: nom, lat/lng: coords, s: status, t: type, c: capacité
        results.append({
            "n": erp['nom'],
            "lat": erp['lat'],
            "lng": erp['lng'],
            "s": status,
            "t": erp['type'],
            "c": erp['capacite']
        })

    # Statistiques globales pour les compteurs du haut
    total_batiments = len(DATABASE)
    # Pourcentage d'impact (utilisé par la barre de survie)
    pct_impact = round((impactes_count / total_batiments) * 100, 1) if total_batiments > 0 else 0
    # Texte de survie (ex: "85%")
    survie_text = f"{int(100 - pct_impact)}%"

    return jsonify({
        "stats": {
            "total": total_batiments,
            "impactes": impactes_count,
            "cap_perdue": cap_perdue,
            "pct": survie_text  # Le front attend une string avec %
        },
        "points": results
    })

# ─── LANCEMENT ───────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, port=5000)