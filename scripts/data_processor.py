import csv
import heapq
import json
import math
import os
import time
import urllib.parse
import urllib.request

import geopandas as gpd
import numpy as np
from scipy.ndimage import median_filter, minimum_filter
from shapely.geometry import Point

# ── Constantes ERP ────────────────────────────────────────────────────────────

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

# ── Paramètres API ────────────────────────────────────────────────────────────

IGN_ALTI_URL = 'https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json'
PPRI_SHP     = '../data/ppri/zones/dataset/n_zone_reg_ppri_033.shp'
BATCH_SIZE   = 50
SLEEP_SEC    = 0.3

# ── Paramètres MNT ───────────────────────────────────────────────────────────

DEM_BBOX     = (44.77, -0.62, 44.92, -0.50)   # min_lat, min_lng, max_lat, max_lng
DEM_STEP_M   = 50                              # résolution en mètres
DEM_CACHE    = '../data/dem_cache.npy'
DEM_META     = '../data/dem_meta.json'

# ── Points Garonne (185 pts, BD TOPO IGN) ────────────────────────────────────

GARONNE_POINTS = [
    (44.770462, -0.511481), (44.772138, -0.511445), (44.773039, -0.511411),
    (44.773815, -0.511734), (44.77458, -0.512052), (44.776166, -0.512976),
    (44.777622, -0.514043), (44.778015, -0.514542), (44.778111, -0.514664),
    (44.778463, -0.515109), (44.780641, -0.516574), (44.781498, -0.516742),
    (44.782102, -0.516859), (44.783693, -0.517049), (44.783731, -0.517053),
    (44.785197, -0.517309), (44.786345, -0.517514), (44.787495, -0.517902),
    (44.787953, -0.518073), (44.788694, -0.518347), (44.79, -0.518301),
    (44.790506, -0.518086), (44.790591, -0.518065), (44.790651, -0.522181),
    (44.790683, -0.51804), (44.790755, -0.522196), (44.79147, -0.517836),
    (44.7915, -0.522287), (44.791989, -0.522468), (44.792388, -0.522614),
    (44.792533, -0.517567), (44.792684, -0.517536), (44.792944, -0.517483),
    (44.79302, -0.522916), (44.79352, -0.517365), (44.793888, -0.517341),
    (44.793931, -0.523478), (44.794047, -0.523551), (44.794217, -0.517318),
    (44.794932, -0.517314), (44.795075, -0.524011), (44.795493, -0.517317),
    (44.79609, -0.524491), (44.796152, -0.524513), (44.796484, -0.517441),
    (44.797581, -0.524994), (44.797736, -0.517789), (44.797758, -0.517797),
    (44.798132, -0.5179), (44.799077, -0.518266), (44.799169, -0.525403),
    (44.799855, -0.518661), (44.80044, -0.525652), (44.800485, -0.525661),
    (44.800568, -0.519064), (44.801455, -0.519663), (44.801836, -0.526065),
    (44.802533, -0.52052), (44.802887, -0.520859), (44.803179, -0.526582),
    (44.803297, -0.521248), (44.80333, -0.52664), (44.803728, -0.521535),
    (44.803833, -0.521605), (44.804522, -0.526908), (44.805358, -0.527101),
    (44.805453, -0.522959), (44.806202, -0.527263), (44.806788, -0.524269),
    (44.807893, -0.526363), (44.808179, -0.527035), (44.808469, -0.528183),
    (44.808736, -0.528336), (44.810524, -0.529372), (44.811156, -0.529652),
    (44.811372, -0.529781), (44.81294, -0.530707), (44.815997, -0.532514),
    (44.816073, -0.53256), (44.816324, -0.532713), (44.819497, -0.534643),
    (44.819956, -0.534901), (44.820079, -0.534981), (44.820531, -0.535273),
    (44.82063, -0.535376), (44.821235, -0.53599), (44.822838, -0.537624),
    (44.823731, -0.538534), (44.823818, -0.53866), (44.825701, -0.541344),
    (44.826448, -0.542375), (44.827334, -0.543708), (44.827437, -0.543861),
    (44.82987, -0.548566), (44.831181, -0.55103), (44.832493, -0.553473),
    (44.832894, -0.554308), (44.833357, -0.555268), (44.834228, -0.556934),
    (44.834992, -0.558311), (44.836223, -0.560295), (44.837279, -0.561748),
    (44.838555, -0.563155), (44.840655, -0.565493), (44.84093, -0.565738),
    (44.841086, -0.565853), (44.841517, -0.566168), (44.842258, -0.566583),
    (44.842928, -0.566833), (44.84453, -0.567414), (44.845533, -0.567691),
    (44.846814, -0.567851), (44.84699, -0.567873), (44.847356, -0.567862),
    (44.847864, -0.56779), (44.848199, -0.56771), (44.848575, -0.5676),
    (44.848948, -0.567384), (44.849414, -0.567135), (44.85002, -0.566725),
    (44.850373, -0.566385), (44.850781, -0.565946), (44.851352, -0.565317),
    (44.852443, -0.56399), (44.853674, -0.562187), (44.854674, -0.560187),
    (44.856634, -0.555476), (44.856668, -0.555396), (44.859866, -0.548746),
    (44.860527, -0.547599), (44.862233, -0.544645), (44.862393, -0.544536),
    (44.864797, -0.542905), (44.866735, -0.541872), (44.866791, -0.541841),
    (44.868525, -0.541193), (44.868778, -0.54112), (44.870213, -0.540702),
    (44.872157, -0.540407), (44.873827, -0.540075), (44.873835, -0.540073),
    (44.873958, -0.540048), (44.874046, -0.540018), (44.874412, -0.539891),
    (44.874422, -0.539888), (44.875513, -0.539456), (44.877127, -0.538321),
    (44.878858, -0.537266), (44.87898, -0.537192), (44.879926, -0.536662),
    (44.880601, -0.536284), (44.882393, -0.535637), (44.883957, -0.535409),
    (44.886538, -0.535298), (44.888875, -0.535238), (44.889111, -0.535256),
    (44.890517, -0.535358), (44.892135, -0.535669), (44.893359, -0.536213),
    (44.893838, -0.536426), (44.893894, -0.53645), (44.894832, -0.536733),
    (44.896285, -0.537219), (44.897202, -0.537507), (44.898118, -0.537795),
    (44.899676, -0.538245), (44.900007, -0.538339), (44.901623, -0.538989),
    (44.903223, -0.539877), (44.90516, -0.540962), (44.906754, -0.542227),
    (44.907732, -0.543007), (44.907885, -0.543127), (44.908879, -0.543726),
    (44.908995, -0.543794), (44.910445, -0.544568), (44.910973, -0.544797),
    (44.911852, -0.545234), (44.912869, -0.545798), (44.913485, -0.546139),
    (44.913953, -0.546458), (44.916694, -0.54787), (44.917884, -0.548333),
    (44.919627, -0.549025), (44.91991, -0.549108),
]


# ── Helpers ───────────────────────────────────────────────────────────────────

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


def fetch_alti_batch(lats_list, lngs_list):
    """Interroge l'API IGN pour une liste de points. Retourne liste d'altitudes."""
    params = urllib.parse.urlencode({
        'lon': ','.join(str(x) for x in lngs_list),
        'lat': ','.join(str(x) for x in lats_list),
        'resource': 'ign_rge_alti_wld',
        'delimiter': ',',
    })
    url = f'{IGN_ALTI_URL}?{params}'
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            data = json.loads(resp.read())
        return [e.get('z', -9999) for e in data.get('elevations', [])]
    except Exception:
        return [-9999] * len(lats_list)


# ── MNT : téléchargement ──────────────────────────────────────────────────────

def build_dem():
    """Télécharge le MNT IGN sur la bbox de Bordeaux et le met en cache."""
    if os.path.exists(DEM_CACHE) and os.path.exists(DEM_META):
        print("  MNT en cache, chargement...")
        dem = np.load(DEM_CACHE)
        with open(DEM_META) as f:
            meta = json.load(f)
        lats = np.array(meta['lats'])
        lngs = np.array(meta['lngs'])
        return dem, lats, lngs

    min_lat, min_lng, max_lat, max_lng = DEM_BBOX
    step_lat = DEM_STEP_M / 111000
    step_lng = DEM_STEP_M / (111000 * math.cos(math.radians((min_lat + max_lat) / 2)))

    lats = np.arange(min_lat, max_lat, step_lat)
    lngs = np.arange(min_lng, max_lng, step_lng)
    nrows, ncols = len(lats), len(lngs)
    total = nrows * ncols

    print(f"  Téléchargement MNT {nrows}×{ncols} = {total:,} cellules (~{math.ceil(total/BATCH_SIZE)*SLEEP_SEC/60:.1f} min)...")

    flat_lats = [lats[r] for r in range(nrows) for _ in range(ncols)]
    flat_lngs = [lngs[c] for _ in range(nrows) for c in range(ncols)]

    dem_flat = []
    for start in range(0, total, BATCH_SIZE):
        batch_lats = flat_lats[start:start + BATCH_SIZE]
        batch_lngs = flat_lngs[start:start + BATCH_SIZE]
        alts = fetch_alti_batch(batch_lats, batch_lngs)
        while len(alts) < len(batch_lats):
            alts.append(-9999)
        dem_flat.extend(alts)
        done = min(start + BATCH_SIZE, total)
        print(f"  {done}/{total} cellules...", end='\r')
        time.sleep(SLEEP_SEC)

    print()
    dem = np.array(dem_flat, dtype=np.float32).reshape(nrows, ncols)
    np.save(DEM_CACHE, dem)
    with open(DEM_META, 'w') as f:
        json.dump({'lats': lats.tolist(), 'lngs': lngs.tolist()}, f)

    return dem, lats, lngs


# ── Flood Fill (Dijkstra) ─────────────────────────────────────────────────────

def compute_flood_connectivity(dem, lats, lngs, garonne_pts):
    """
    Calcule pour chaque cellule le niveau NGF minimum auquel l'eau
    de la Garonne peut l'atteindre (en tenant compte de la topographie).
    Retourne un tableau 2D de mêmes dimensions que dem.
    Cellules inaccessibles = np.inf.
    """
    nrows, ncols = dem.shape
    flood = np.full((nrows, ncols), np.inf, dtype=np.float64)
    step_lat = lats[1] - lats[0]
    step_lng = lngs[1] - lngs[0]

    pq = []  # (flood_level, row, col)

    # Initialisation : cellules de la Garonne
    for glat, glng in garonne_pts:
        r = int(round((glat - lats[0]) / step_lat))
        c = int(round((glng - lngs[0]) / step_lng))
        r = max(0, min(nrows - 1, r))
        c = max(0, min(ncols - 1, c))
        alt = float(dem[r, c])
        if alt > -9000:
            level = alt
            if level < flood[r, c]:
                flood[r, c] = level
                heapq.heappush(pq, (level, r, c))

    # Dijkstra
    while pq:
        level, r, c = heapq.heappop(pq)
        if level > flood[r, c]:
            continue  # entrée périmée
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < nrows and 0 <= nc < ncols:
                alt_n = float(dem[nr, nc])
                if alt_n <= -9000:
                    continue
                # Pour atteindre le voisin, l'eau doit monter jusqu'à
                # max(niveau actuel, altitude du voisin)
                new_level = max(level, alt_n)
                if new_level < flood[nr, nc]:
                    flood[nr, nc] = new_level
                    heapq.heappush(pq, (new_level, nr, nc))

    return flood


def get_flood_req(lat, lng, flood_connectivity, lats, lngs):
    """Retourne le niveau NGF requis pour inonder ce point (None si inaccessible)."""
    step_lat = lats[1] - lats[0]
    step_lng = lngs[1] - lngs[0]
    r = int(round((lat - lats[0]) / step_lat))
    c = int(round((lng - lngs[0]) / step_lng))
    r = max(0, min(flood_connectivity.shape[0] - 1, r))
    c = max(0, min(flood_connectivity.shape[1] - 1, c))
    val = flood_connectivity[r, c]
    return None if np.isinf(val) else round(float(val), 2)


# ── PPRI (bonus affichage popup) ──────────────────────────────────────────────

ZONES_EXCLUES = {'Réseau hydraulique', 'Zone en eau - Réseau hydrographique'}

def load_ppri():
    gdf = gpd.read_file(PPRI_SHP, engine='fiona')
    return gdf.to_crs(epsg=4326)

def assign_zone_ppri(rows, ppri):
    ppri_filtered = ppri[~ppri['nom'].isin(ZONES_EXCLUES)]
    points = gpd.GeoDataFrame(
        {'idx': range(len(rows))},
        geometry=[Point(r['lng'], r['lat']) for r in rows],
        crs='EPSG:4326',
    )
    joined = gpd.sjoin(points, ppri_filtered[['codezone', 'nom', 'geometry']], how='left', predicate='within')
    joined = joined[~joined.index.duplicated(keep='first')].reindex(range(len(rows)))
    return joined['nom'].tolist()


# ── Pipeline principal ────────────────────────────────────────────────────────

# 1. Lecture et filtrage ERP
output_rows = []
with open('../data/raw_bor_erp.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    next(reader)
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
        if lat is None:
            continue
        try:
            capacite = int(float(capacite_raw)) if capacite_raw else 0
        except ValueError:
            capacite = 0
        output_rows.append({'nom': nom, 'lat': lat, 'lng': lng,
                            'type': TYPE_LABELS[type_erp], 'capacite': capacite})

print(f"{len(output_rows)} établissements chargés.")

# 2. MNT + Flood Fill
print("Construction du MNT...")
dem, lats, lngs = build_dem()
# Lissage médian 3×3 pour supprimer le bruit d'échantillonnage (routes, trottoirs...)
# Remplacer les nodata avant le filtre, puis restaurer
nodata_mask = dem <= -9000
dem_work = dem.copy()
dem_work[nodata_mask] = np.nan
# Remplir les nan par interpolation simple (valeur voisine) pour le filtre
from numpy import nanmean
for _ in range(3):
    nan_pos = np.argwhere(np.isnan(dem_work))
    for r, c in nan_pos:
        neighbors = dem_work[max(0,r-1):r+2, max(0,c-1):c+2]
        val = nanmean(neighbors)
        if not np.isnan(val):
            dem_work[r, c] = val
# Filtre minimum 3×3 : abaisse les pics isolés (remblais DEM artificiels)
# puis médian pour lisser sans créer de nouveaux artefacts
dem_smoothed = minimum_filter(median_filter(dem_work, size=3), size=3).astype(np.float32)
dem_smoothed[nodata_mask] = -9999
dem = dem_smoothed
print(f"  MNT {dem.shape[0]}×{dem.shape[1]} chargé et lissé. Lancement du flood fill (Dijkstra)...")
flood_connectivity = compute_flood_connectivity(dem, lats, lngs, GARONNE_POINTS)
reachable = np.isfinite(flood_connectivity).sum()
print(f"  Flood fill terminé : {reachable:,} cellules accessibles depuis la Garonne.")

# 3. Attribution flood_level_req à chaque ERP
print("Attribution flood_level_req aux ERP...")
for row in output_rows:
    row['flood_level_req'] = get_flood_req(row['lat'], row['lng'],
                                           flood_connectivity, lats, lngs)

# 4. Altitude IGN (pour affichage popup)
print("Récupération des altitudes IGN...")
total = len(output_rows)
for start in range(0, total, BATCH_SIZE):
    batch = output_rows[start:start + BATCH_SIZE]
    alts = fetch_alti_batch([r['lat'] for r in batch], [r['lng'] for r in batch])
    for row, alt in zip(batch, alts):
        row['altitude'] = round(alt, 2)
    print(f"  {min(start+BATCH_SIZE, total)}/{total} altitudes...", end='\r')
    time.sleep(SLEEP_SEC)
print()

# 5. Zone PPRI (pour affichage popup)
print("Chargement PPRI...")
ppri = load_ppri()
zones = assign_zone_ppri(output_rows, ppri)
for row, zone in zip(output_rows, zones):
    row['zone_ppri'] = zone if isinstance(zone, str) else None

# 6. Export
with open('../data/bor_erp_managed.csv', 'w', newline='', encoding='utf-8') as outfile:
    fieldnames = ['nom', 'lat', 'lng', 'type', 'capacite', 'flood_level_req', 'altitude', 'zone_ppri']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='|')
    writer.writeheader()
    writer.writerows(output_rows)

print(f"{len(output_rows)} établissements exportés dans bor_erp_managed.csv")
