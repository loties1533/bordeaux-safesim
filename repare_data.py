import csv
import math
import os

# --- CONFIGURATION DES CHEMINS ---
# Le fichier brut doit être dans ton dossier data
source = 'data/raw_bor_erp.csv'
# Le fichier nettoyé sera créé ici pour app.py
destination = 'data/bor_erp_managed.csv'

TYPES_UTILES = ['R', 'U', 'J', 'X', 'W', 'L', 'O', 'S', 'M', 'T']
TYPE_LABELS = {
    'R': 'Écoles / collèges / lycées',
    'U': 'Hôpitaux / cliniques',
    'J': 'Maisons de retraite / handicapés',
    'X': 'Gymnases / sports couverts',
    'W': 'Mairies / administrations',
    'L': 'Salles de spectacle / conférences',
    'O': 'Hôtels / hébergements',
    'S': 'Bibliothèques / médiathèques',
    'M': 'Centres commerciaux',
    'T': "Halls d'exposition",
}

GARONNE_POINTS = [
    (44.862, -0.612), (44.854, -0.598), (44.845, -0.573),
    (44.838, -0.564), (44.830, -0.556), (44.820, -0.548),
]

CANTON_SEUIL_MAP = [
    (['bacalan', 'bastide', 'quai', 'benauge'], 2),
    (['capucin', 'saint-michel', 'st michel', 'victoire', 'ste croix', 'sainte-croix'], 3),
    (['meriadeck', 'mériadeck', 'chartrons', 'hotel de ville', 'quinconces', 'grand parc'], 5),
    (['seurin', 'fondaudege', 'fondaudège', 'cauderan', 'caudéran', 'saint-augustin', 'st augustin'], 7),
    (['cenon', 'floirac', 'lormont', 'bouliac'], 9),
]

def distance_km(lat1, lng1, lat2, lng2):
    dlat = (lat2 - lat1) * 111
    dlng = (lng2 - lng1) * 111 * math.cos(math.radians(lat1))
    return math.sqrt(dlat**2 + dlat**2)

def get_seuil_coords(lat, lng):
    dist = min(distance_km(lat, lng, p[0], p[1]) for p in GARONNE_POINTS)
    if dist < 0.5: return 1
    if dist < 1.0: return 2
    if dist < 1.8: return 3
    if dist < 2.8: return 4
    if dist < 3.8: return 5
    if dist < 5.0: return 7
    return 9

def get_seuil_canton(canton):
    canton_lower = canton.lower()
    for keywords, seuil in CANTON_SEUIL_MAP:
        if any(k in canton_lower for k in keywords): return seuil
    return None

def get_seuil(canton, lat, lng):
    if canton:
        seuil = get_seuil_canton(canton)
        if seuil is not None: return seuil
    return get_seuil_coords(lat, lng)

def parse_coords(geometrie):
    if not geometrie.strip(): return None, None
    parts = geometrie.split(',')
    if len(parts) != 2: return None, None
    try: return float(parts[0].strip()), float(parts[1].strip())
    except ValueError: return None, None

output_rows = []

# --- EXÉCUTION ---
if not os.path.exists(source):
    print(f"❌ ERREUR : Le fichier {source} n'est pas dans le dossier data !")
    print("Vérifie que raw_bor_erp.csv est bien dans bordeaux-safesim/data/")
else:
    with open(source, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)
        for row in reader:
            if len(row) < 13: continue
            type_erp = row[4].strip()
            if type_erp not in TYPES_UTILES: continue
            nom = row[1].strip().title()
            canton = row[9].strip()
            capacite_raw = row[11].strip()
            geometrie = row[12].strip()
            lat, lng = parse_coords(geometrie)
            if lat is None or lng is None: continue
            try: capacite = int(float(capacite_raw)) if capacite_raw else 0
            except ValueError: capacite = 0
            
            output_rows.append({
                'nom': nom, 'lat': lat, 'lng': lng,
                'type': TYPE_LABELS[type_erp], 'capacite': capacite,
                'seuil': get_seuil(canton, lat, lng),
            })

    with open(destination, 'w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['nom', 'lat', 'lng', 'type', 'capacite', 'seuil']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter="|")
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"✅ SUCCÈS : {len(output_rows)} établissements créés dans {destination}")