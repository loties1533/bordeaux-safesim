import csv
import math

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
# Points extraits du tronçon centerline BD Carthage 2017 (IGN/SANDRE),
# reprojetés Lambert-93 → WGS84, échantillonnés tous les ~400m.
GARONNE_POINTS = [
    (44.781493, -0.517437),
    (44.786596, -0.520592),
    (44.790417, -0.522796),
    (44.793928, -0.524493),
    (44.798034, -0.525828),
    (44.801932, -0.526837),
    (44.805729, -0.527916),
    (44.809299, -0.529097),
    (44.812959, -0.530599),
    (44.816312, -0.532490),
    (44.819924, -0.534802),
    (44.823562, -0.538530),
    (44.826445, -0.542207),
    (44.829595, -0.547744),
    (44.832856, -0.554161),
    (44.836275, -0.559714),
    (44.839326, -0.563477),
    (44.842458, -0.566220),
    (44.846642, -0.568006),
    (44.850106, -0.566351),
    (44.852893, -0.563005),
    (44.857032, -0.554159),
    (44.859685, -0.548716),
    (44.862579, -0.544751),
    (44.866245, -0.542207),
    (44.870818, -0.541164),
    (44.874460, -0.539567),
    (44.878296, -0.537410),
    (44.881800, -0.535945),
    (44.886720, -0.535362),
    (44.891742, -0.536050),
    (44.895270, -0.537106),
    (44.898750, -0.538615),
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

with open('../data/raw_bor_erp.csv', 'r', encoding='utf-8') as csvfile:
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

        output_rows.append({
            'nom': nom,
            'lat': lat,
            'lng': lng,
            'type': TYPE_LABELS[type_erp],
            'capacite': capacite,
            'seuil': get_seuil_coords(lat, lng),
        })

with open('../data/bor_erp_managed.csv', 'w', newline='', encoding='utf-8') as outfile:
    fieldnames = ['nom', 'lat', 'lng', 'type', 'capacite', 'seuil']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter="|")
    writer.writeheader()
    writer.writerows(output_rows)

print(f"{len(output_rows)} établissements exportés dans bor_erp_managed.csv")
