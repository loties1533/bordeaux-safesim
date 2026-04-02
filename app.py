import os
import pandas as pd
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

DATA_PATH = os.path.join('data', 'bor_erp_managed.csv')
IRIS_PATH = os.path.join('data', 'raw', 'se_iri24_s.csv')
TBM_PATH = os.path.join('data', 'raw', 'sv_chem_l_sv_tronc_l.csv')

MAPPING_TRAM = {
    "2173530": "Tram A", "2173533": "Tram A",
    "2173835": "Tram B", "2173836": "Tram B",
    "2173851": "Tram C", "2173852": "Tram C",
    "2173860": "Tram D"
}

def get_real_population():
    if os.path.exists(IRIS_PATH):
        try:
            df_insee = pd.read_csv(IRIS_PATH, sep=';')
            df_bdx = df_insee[(df_insee['insee'] == 33063) & (df_insee['iris'] != 330630000)]
            col_pop = [c for c in df_bdx.columns if 'pop' in c.lower()][0]
            return df_bdx[col_pop].sum()
        except:
            pass
    return 261804

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/simulate')
def simulate():
    try:
        niveau = float(request.args.get('niveau', 0))
    except:
        niveau = 0.0

    if not os.path.exists(DATA_PATH):
        return jsonify({"error": "Data missing"})
    
    df_erp = pd.read_csv(DATA_PATH, sep="|")
    pop_totale_insee = get_real_population()

    lignes_hs = []
    if os.path.exists(TBM_PATH) and niveau > 4.5:
        df_tbm = pd.read_csv(TBM_PATH, sep=';')
        troncons_quais = [3922, 2794, 1514, 1282, 11670]
        mask = df_tbm['rs_sv_tronc_l'].isin(troncons_quais)
        
        # --- LA MODIF EST ICI ---
        ids = df_tbm[mask]['rs_sv_chem_l'].unique().astype(str)
        noms_nets = set()
        for i in ids:
            nom = MAPPING_TRAM.get(i, f"Tram {i[-4:]}")
            noms_nets.add(nom)
        lignes_hs = sorted(list(noms_nets))
        # --- FIN DE LA MODIF ---

    points = []
    lieux_isoles_noms = []
    capa_impactee = 0
    capa_totale = df_erp['capacite'].sum()

    for i, row in df_erp.iterrows():
        alt_sol = float(row['altitude'])
        is_flooded = niveau >= alt_sol
        
        if is_flooded:
            capa_impactee += row['capacite']
            lieux_isoles_noms.append(row['nom'])
        
        points.append({
            "id": str(i),
            "lat": row['lat'],
            "lon": row['lng'],
            "nom": row['nom'],
            "status": "danger" if is_flooded else "ok",
            "type": row['type'],
            "alt": alt_sol,
            "capacite": int(row['capacite'])
        })

    ratio = (capa_impactee / capa_totale) if capa_totale > 0 else 0
    
    return jsonify({
        "statistiques": {
            "total_impacte": int(ratio * pop_totale_insee),
            "pourcentage_impact": f"{round(ratio * 100, 1)}%",
            "nb_lieux_isoles": len(lieux_isoles_noms)
        },
        "transport": {
            "lignes_touchees": lignes_hs,
            "status": "ALERTE" if lignes_hs else "NORMAL",
            "lieux_isoles": lieux_isoles_noms[:20]
        },
        "points": points
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)