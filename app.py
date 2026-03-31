from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

#  Chargement de la data 
DATA_PATH = os.path.join('data', 'erp_managed.json')

# JSON tests en attendant le Dev 1
FAKE_DATA = [
    {"nom": "Gymnase Barbey",    "lat": 44.8268, "lng": -0.5703, "seuil": 3, "capacite": 500,  "type": "Sport"},
    {"nom": "École Achard",      "lat": 44.8612, "lng": -0.5445, "seuil": 6, "capacite": 300,  "type": "Scolaire"},
    {"nom": "Mairie Bordeaux",   "lat": 44.8412, "lng": -0.5733, "seuil": 2, "capacite": 200,  "type": "Administratif"},
    {"nom": "Gymnase Bacalan",   "lat": 44.8712, "lng": -0.5603, "seuil": 1, "capacite": 800,  "type": "Sport"},
    {"nom": "École Meriadeck",   "lat": 44.8378, "lng": -0.5812, "seuil": 5, "capacite": 400,  "type": "Scolaire"},
    {"nom": "Stade Chaban",      "lat": 44.8645, "lng": -0.5578, "seuil": 4, "capacite": 3000, "type": "Sport"},
    {"nom": "École Saint-Louis", "lat": 44.8334, "lng": -0.5689, "seuil": 7, "capacite": 250,  "type": "Scolaire"},
    {"nom": "Gymnase Bastide",   "lat": 44.8389, "lng": -0.5512, "seuil": 2, "capacite": 600,  "type": "Sport"},
    {"nom": "Médiathèque",       "lat": 44.8456, "lng": -0.5734, "seuil": 8, "capacite": 350,  "type": "Culture"},
    {"nom": "Centre Commercial", "lat": 44.8523, "lng": -0.5634, "seuil": 5, "capacite": 2000, "type": "Commerce"}
]

# Charge le vrai JSON si dispo, sinon utilise fake data pour les tests
if os.path.exists(DATA_PATH):
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        DATABASE = json.load(f)
    print("✅ Vraie data chargée :", len(DATABASE), "bâtiments")
else:
    DATABASE = FAKE_DATA
    print("⚠️  Data bidon chargée (en attente Dev 1)")


# Route principale 
@app.route('/api/simulate', methods=['GET'])
def simulate():

    # Récupérer le niveau du slider
    level = int(request.args.get('level', 0))

    results   = []
    impactes  = 0
    cap_perdue = 0

    # Algorithme de simulation
    for erp in DATABASE:
        if level >= erp['seuil']:
            status = "danger"
            impactes  += 1
            cap_perdue += erp.get('capacite', 0)
        else:
            status = "ok"

        results.append({
            "n":   erp['nom'],
            "lat": erp['lat'],
            "lng": erp['lng'],
            "s":   status,
            "t":   erp.get('type', '')
        })

    #  Calcul des stats
    total = len(DATABASE)
    pct   = round((impactes / total) * 100, 1) if total > 0 else 0

    #  Renvoyer le JSON au Front
    return jsonify({
        "stats": {
            "total":        total,
            "impactes":     impactes,
            "cap_perdue":   cap_perdue,
            "pct":          pct
        },
        "points": results
    })


# Route de test
@app.route('/')
def home():
    return "🧠 Cerveau opérationnel — /api/simulate?level=5"


# Lancement de l'app Flask
if __name__ == '__main__':
    app.run(debug=True, port=5000)