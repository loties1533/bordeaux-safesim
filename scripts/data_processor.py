import csv
import time
import urllib.request
import urllib.parse
import json

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

IGN_ALTI_URL = 'https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json'
BATCH_SIZE = 50   # points par requête
SLEEP_BETWEEN_BATCHES = 0.3  # secondes


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


def fetch_altitudes(rows):
    """Interroge l'API IGN par batch (POST) et retourne une liste d'altitudes (même ordre que rows)."""
    altitudes = []
    total = len(rows)

    for start in range(0, total, BATCH_SIZE):
        batch = rows[start:start + BATCH_SIZE]
        lats = ','.join(str(r['lat']) for r in batch)
        lngs = ','.join(str(r['lng']) for r in batch)

        params = urllib.parse.urlencode({
            'lon': lngs,
            'lat': lats,
            'resource': 'ign_rge_alti_wld',
            'delimiter': ',',
        })
        url = f'{IGN_ALTI_URL}?{params}'

        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
                data = json.loads(resp.read())
            batch_alts = [e.get('z', -9999) for e in data.get('elevations', [])]
            while len(batch_alts) < len(batch):
                batch_alts.append(-9999)
        except Exception as exc:
            print(f"  Erreur batch {start}–{start+len(batch)}: {exc}")
            batch_alts = [-9999] * len(batch)

        altitudes.extend(batch_alts)
        done = min(start + BATCH_SIZE, total)
        print(f"  {done}/{total} altitudes récupérées...", end='\r')
        time.sleep(SLEEP_BETWEEN_BATCHES)

    print()
    return altitudes


# ── Lecture et filtrage du CSV source ────────────────────────────────────────

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
            continue

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
        })

print(f"{len(output_rows)} établissements chargés. Récupération des altitudes IGN...")

# ── Enrichissement altimétrique ───────────────────────────────────────────────

altitudes = fetch_altitudes(output_rows)

for row, alt in zip(output_rows, altitudes):
    row['altitude'] = round(alt, 2)

# ── Export ────────────────────────────────────────────────────────────────────

with open('../data/bor_erp_managed.csv', 'w', newline='', encoding='utf-8') as outfile:
    fieldnames = ['nom', 'lat', 'lng', 'type', 'capacite', 'altitude']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='|')
    writer.writeheader()
    writer.writerows(output_rows)

print(f"{len(output_rows)} établissements exportés dans bor_erp_managed.csv")
