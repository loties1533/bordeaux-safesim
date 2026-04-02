import csv
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH  = os.path.join(BASE_DIR, 'data', 'raw_bor_erp.csv')
OUT_DATA_PATH  = os.path.join(BASE_DIR, 'data', 'bor_erp_managed.csv')
INSEE_PATH     = os.path.join(BASE_DIR, 'data', 'raw', 'donnees_communes.csv')

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

# Communes Bordeaux Métropole : code INSEE → population (INSEE RP 2021)
COMMUNES_BM = {
    '33063': 259809,  # Bordeaux
    '33281': 70362,   # Mérignac
    '33522': 62000,   # Pessac
    '33550': 42000,   # Talence
    '33249': 24000,   # Le Bouscat
    '33032': 27000,   # Bègles
    '33119': 19800,   # Eysines
    '33270': 22500,   # Lormont
    '33075': 16500,   # Bruges
    '33167': 17500,   # Floirac
}

GARONNE_POINTS = [
    (44.882, -0.565), (44.878, -0.564), (44.874, -0.563),
    (44.870, -0.563), (44.866, -0.563), (44.862, -0.562),
    (44.858, -0.562), (44.854, -0.561), (44.850, -0.560),
    (44.846, -0.559), (44.843, -0.558), (44.840, -0.558),
    (44.837, -0.557), (44.834, -0.556), (44.831, -0.555),
    (44.828, -0.553), (44.825, -0.552), (44.822, -0.550),
    (44.819, -0.549), (44.815, -0.547), (44.811, -0.545),
    (44.807, -0.543), (44.803, -0.541), (44.799, -0.539),
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
        "Halls d'exposition": 0,
    }
    return criticites.get(type_label, 0)


def is_refuge(type_label, seuil):
    refuge_types = ['Gymnases / sports couverts', 'Écoles / collèges / lycées', 'Mairies / administrations']
    return type_label in refuge_types and seuil >= 6


def find_commune(lat, lng):
    """Trouve la commune la plus proche parmi les communes BM."""
    best_code = '33063'
    best_dist = float('inf')
    centres = {
        '33063': (44.8378, -0.5792),
        '33281': (44.8378, -0.6436),
        '33522': (44.8067, -0.6306),
        '33550': (44.8056, -0.5906),
        '33249': (44.8644, -0.6003),
        '33032': (44.8083, -0.5508),
        '33119': (44.8847, -0.6408),
        '33270': (44.8728, -0.5236),
        '33075': (44.8853, -0.6003),
        '33167': (44.8303, -0.5200),
    }
    for code, (clat, clng) in centres.items():
        d = distance_km(lat, lng, clat, clng)
        if d < best_dist:
            best_dist = d
            best_code = code
    return best_code


def load_insee_population():
    """Charge la population depuis donnees_communes.csv — colonne CODCOM + PMUN."""
    pop = {}
    if not os.path.exists(INSEE_PATH):
        print(f"⚠️  INSEE absent ({INSEE_PATH}) — utilisation des valeurs hardcodées")
        return {}
    try:
        with open(INSEE_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                codcom = row.get('CODCOM', '').strip()
                pmun   = row.get('PMUN', '').strip()
                if codcom and pmun:
                    try:
                        pop[codcom] = int(float(pmun))
                    except ValueError:
                        pass
        print(f"✅ INSEE : {len(pop)} communes chargées")
    except Exception as e:
        print(f"⚠️  Erreur lecture INSEE : {e}")
    return pop


def get_population(lat, lng, insee_data):
    """Retourne la population de la commune la plus proche."""
    code = find_commune(lat, lng)
    if code in insee_data:
        return insee_data[code]
    return COMMUNES_BM.get(code, 259809)


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


# ── Chargement INSEE
insee_data  = load_insee_population()
output_rows = []

with open(RAW_DATA_PATH, 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    next(reader)

    for row in reader:
        if len(row) < 13:
            continue

        type_erp = row[4].strip()
        if type_erp not in TYPES_UTILES:
            continue

        nom          = row[1].strip().title()
        capacite_raw = row[11].strip()
        geometrie    = row[12].strip()

        lat, lng = parse_coords(geometrie)
        if lat is None:
            continue

        try:
            capacite = int(float(capacite_raw)) if capacite_raw else 0
        except ValueError:
            capacite = 0

        type_label = TYPE_LABELS[type_erp]
        seuil      = get_seuil_coords(lat, lng)
        population = get_population(lat, lng, insee_data)

        output_rows.append({
            'nom':        nom,
            'lat':        lat,
            'lng':        lng,
            'type':       type_label,
            'capacite':   capacite,
            'seuil':      seuil,
            'criticite':  get_criticite(type_label),
            'est_refuge': 'oui' if is_refuge(type_label, seuil) else 'non',
            'population': population,
        })

fieldnames = ['nom', 'lat', 'lng', 'type', 'capacite', 'seuil', 'criticite', 'est_refuge', 'population']

with open(OUT_DATA_PATH, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter="|")
    writer.writeheader()
    writer.writerows(output_rows)

print(f"✅ {len(output_rows)} établissements exportés dans bor_erp_managed.csv")
print(f"📊 Colonnes : {', '.join(fieldnames)}")