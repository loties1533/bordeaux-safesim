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

# ─── DÉFINITIONS RÉSILIENCE CLIMATIQUE ────────────────────────────────────
# Criticité par type d'établissement (pour évacuation/priorité)
CRITICAL_LEVELS = {
    'Hôpitaux / cliniques': 9,          # Priorité absolue (patients nécessitent suivi médical)
    'Maisons de retraite / handicapés': 8,  # Personnes vulnérables
    'Écoles / collèges / lycées': 7,    # Enfants, potentiellement refuge
    'Gymnases / sports couverts': 6,    # Refuge/évacuation possible
    'Mairies / administrations': 5,     # Command center potentiel
    'Salles de spectacle / conférences': 4,  # Non essentiel
    'Hôtels / hébergements': 3,         # Public de passage
    'Centres commerciaux': 2,           # Perte économique
    'Bibliothèques / médiathèques': 1,  # Support communautaire faible
    'Halls d\'exposition': 0,           # Non prioritaire
}

# Types pouvant servir de refuges (seuil >= 6)
REFUGE_TYPES = ['Gymnases / sports couverts', 'Écoles / collèges / lycées', 'Mairies / administrations']
REFUGE_SEUIL_MIN = 6

FAKE_DATA = [
    {"nom": "MODE TEST : Gymnase Barbey", "lat": 44.8268, "lng": -0.5703, "seuil": 3, "capacite": 500, "type": "Gymnases / sports couverts"},
    {"nom": "MODE TEST : École Achard", "lat": 44.8612, "lng": -0.5445, "seuil": 6, "capacite": 300, "type": "Écoles / collèges / lycées"}
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

# ─── CALCULS RÉSILIENCE ──────────────────────────────────────────────────
def compute_resilience_stats():
    """Calcule statistiques de résilience : refuges, capacité, etc."""
    refuges = [b for b in DATABASE if b['type'] in REFUGE_TYPES and b['seuil'] >= REFUGE_SEUIL_MIN]
    refuge_capacity = sum(b['capacite'] for b in refuges)
    return {
        'nb_refuges': len(refuges),
        'refuge_capacity': refuge_capacity,
    }

RESILIENCE = compute_resilience_stats()
print(f"🟦 REFUGES : {RESILIENCE['nb_refuges']} lieux, capacité {RESILIENCE['refuge_capacity']} personnes")

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
    critical_impacted = 0  # Compter bâtiments critiques en danger
    refuges_active = []    # Refuges disponibles (pas en danger)

    for erp in DATABASE:
        # LOGIQUE DE CRISE : niveau d'eau >= seuil du bâtiment ?
        if level >= erp['seuil']:
            status = "danger"
            impactes_count += 1
            cap_perdue += erp['capacite']
            # Compter criticité si en danger
            if erp['type'] in CRITICAL_LEVELS and CRITICAL_LEVELS[erp['type']] >= 8:
                critical_impacted += 1
        else:
            status = "ok"
            # Refuges en sécurité
            if erp['type'] in REFUGE_TYPES and erp['seuil'] >= REFUGE_SEUIL_MIN:
                refuges_active.append(erp)

        # On renvoie les clés simplifiées pour économiser de la bande passante
        # n: nom, lat/lng: coords, s: status, t: type, c: capacité, crit: criticité
        criticite = CRITICAL_LEVELS.get(erp['type'], 0)
        results.append({
            "n": erp['nom'],
            "lat": erp['lat'],
            "lng": erp['lng'],
            "s": status,
            "t": erp['type'],
            "c": erp['capacite'],
            "crit": criticite
        })

    # Statistiques globales pour les compteurs du haut
    total_batiments = len(DATABASE)
    # Pourcentage d'impact (utilisé par la barre de survie)
    pct_impact = round((impactes_count / total_batiments) * 100, 1) if total_batiments > 0 else 0
    # Texte de survie (ex: "85%")
    survie_text = f"{int(100 - pct_impact)}%"
    # Refuges capacité active
    refuge_cap_active = sum(r['capacite'] for r in refuges_active)

    return jsonify({
        "stats": {
            "total": total_batiments,
            "impactes": impactes_count,
            "cap_perdue": cap_perdue,
            "pct": survie_text,  # Le front attend une string avec %
            "critical_count": critical_impacted,  # Bâtiments critiques en danger (hôpitaux, maisons retraite)
            "refuges_available": len(refuges_active),  # Nombre de refuges en sécurité
            "refuge_capacity": refuge_cap_active  # Places en refuges disponibles
        },
        "points": results
    })

# ─── LANCEMENT ───────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, port=5000)