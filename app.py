from flask import Flask, render_template, jsonify, request
import pandas as pd

app = Flask(__name__)

# Charge le fichier propre (généré par Dev 1)
# Pour tester, on crée un mini dataframe si le fichier n'existe pas encore
try:
    df_erp = pd.read_csv('data/processed/erp_managed.csv')
except:
    df_erp = pd.DataFrame(columns=['id', 'nom', 'lat', 'lon', 'seuil_critique', 'capacite'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/simulate')
def simulate():
    niveau = float(request.args.get('niveau', 0))
    
    # LOGIQUE DE SIMULATION (Dev 2 à améliorer)
    points = []
    total_impacte = 0
    
    # Simulation bidon pour le test
    for index, row in df_erp.iterrows():
        status = "ok"
        if niveau >= row['seuil_critique']:
            status = "danger"
            total_impacte += row['capacite']
            
        points.append({
            "id": row['id'],
            "lat": row['lat'],
            "lon": row['lon'],
            "nom": row['nom'],
            "status": status
        })

    return jsonify({
        "statistiques": {
            "total_impacte": int(total_impacte),
            "pourcentage_survie": f"{max(0, 100 - (niveau * 10))}%"
        },
        "points": points
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)