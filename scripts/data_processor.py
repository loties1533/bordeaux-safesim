import csv
import math
import os

# Base path du projet, permet d'exécuter le script depuis n'importe où
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(BASE_DIR, 'data', 'raw_bor_erp.csv')
OUT_DATA_PATH = os.path.join(BASE_DIR, 'data', 'bor_erp_managed.csv')

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

# Points de référence sur la Garonne (rive gauche, du nord au sud)
GARONNE_POINTS = [
    (44.882, -0.565),  # Garonne amont nord
    (44.878, -0.564),  # Bacalan très nord
    (44.874, -0.563),  # Pont Chaban nord
    (44.870, -0.563),  # Pont Chaban
    (44.866, -0.563),  # Bacalan nord
    (44.862, -0.562),  # Bacalan
    (44.858, -0.562),  # Bacalan sud
    (44.854, -0.561),  # Chartrons nord
    (44.850, -0.560),  # Chartrons
    (44.846, -0.559),  # Chartrons sud
    (44.843, -0.558),  # Quais Chartrons extrême sud
    (44.840, -0.558),  # Miroir d'eau
    (44.837, -0.557),  # Quais centre
    (44.834, -0.556),  # Quais centre sud
    (44.831, -0.555),  # Quais milieu
    (44.828, -0.553),  # Quais Saint-Michel
    (44.825, -0.552),  # Saint-Michel sud
    (44.822, -0.550),  # Quais sud nord
    (44.819, -0.549),  # Quais sud
    (44.815, -0.547),  # Quais sud extrême
    (44.811, -0.545),  # Quais très sud
    (44.807, -0.543),  # Garonne aval nord
    (44.803, -0.541),  # Garonne aval
    (44.799, -0.539),  # Garonne aval sud
]

def distance_km(lat1, lng1, lat2, lng2):
    dlat = (lat2 - lat1) * 111
    dlng = (lng2 - lng1) * 111 * math.cos(math.radians(lat1))
    return math.sqrt(dlat**2 + dlng**2)


def get_seuil_coords(lat, lng):
    dist = min(distance_km(lat, lng, p[0], p[1]) for p in GARONNE_POINTS)
    if dist < 0.25: return 1
    if dist < 0.50: return 2
    if dist < 0.80: return 3
    if dist < 1.20: return 4
    if dist < 1.70: return 5
    if dist < 2.40: return 6
    if dist < 3.20: return 7
    if dist < 4.50: return 8
    return 9


def get_criticite(type_label):
    """Retourne le niveau de criticité (0-9) par type d'établissement"""
    criticites = {
        'Hôpitaux / cliniques': 9,
        'Maisons de retraite / handicapés': 8,
        'Écoles / collèges / lycées': 7,
        'Gymnases / sports couverts': 6,
        'Mairies / administrations': 5,
        'Salles de spectacle / conférences': 4,
        'Hôtels / hébergements': 3,
        'Centres commerciaux': 2,
        'Bibliothèques / médiathèques': 1,
        'Halls d\'exposition': 0,
    }
    return criticites.get(type_label, 0)


def is_refuge(type_label, seuil):
    """Détermine si un bâtiment peut servir de refuge"""
    refuge_types = ['Gymnases / sports couverts', 'Écoles / collèges / lycées', 'Mairies / administrations']
    return type_label in refuge_types and seuil >= 6



def parse_coords(geometrie):
    if not geometrie.strip():
        return None, None
    parts = geometrie.split(',')
    if len(parts) != 2:
        return None, None
    try:
        return float(parts[0].strip()), float(parts[1].strip())
    except ValueError:
        return None, None


output_rows = []

with open(RAW_DATA_PATH, 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    next(reader)  # sauter l'en-tête

    for row in reader:
        if len(row) < 13:
            continue

        type_erp = row[4].strip()
        if type_erp not in TYPES_UTILES:
            continue

        nom = row[1].strip().title()
        capacite_raw = row[11].strip()
        geometrie = row[12].strip()

        lat, lng = parse_coords(geometrie)
        if lat is None or lng is None:
            continue  # ignorer les lignes sans coordonnées

        try:
            capacite = int(float(capacite_raw)) if capacite_raw else 0
        except ValueError:
            capacite = 0

        type_label = TYPE_LABELS[type_erp]
        seuil = get_seuil_coords(lat, lng)
        
        output_rows.append({
            'nom': nom,
            'lat': lat,
            'lng': lng,
            'type': type_label,
            'capacite': capacite,
            'seuil': seuil,
            'criticite': get_criticite(type_label),
            'est_refuge': 'oui' if is_refuge(type_label, seuil) else 'non',
        })

with open(OUT_DATA_PATH, 'w', newline='', encoding='utf-8') as outfile:
    fieldnames = ['nom', 'lat', 'lng', 'type', 'capacite', 'seuil', 'criticite', 'est_refuge']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter="|")
    writer.writeheader()
    writer.writerows(output_rows)

print(f"✅ {len(output_rows)} établissements exportés dans bor_erp_managed.csv")
print(f"📊 Colonnes : {', '.join(fieldnames)}")
