import csv
import math
import os

# --- CONFIGURATION ---
# On cible le fichier que app.py lit en temps réel
SOURCE = 'data/bor_erp_managed.csv'
DESTINATION = 'data/bor_erp_managed.csv' 

# Liste complète des 11 points pour couvrir toute la courbe de la Garonne
GARONNE_POINTS = [
    (44.870, -0.555), (44.862, -0.612), (44.858, -0.585), 
    (44.854, -0.598), (44.845, -0.573), (44.840, -0.568),
    (44.838, -0.564), (44.834, -0.560), (44.830, -0.556), 
    (44.825, -0.552), (44.820, -0.548)
]

def distance_km(lat1, lng1, lat2, lng2):
    # Formule corrigée (dlat**2 + dlng**2)
    dlat = (lat2 - lat1) * 111
    dlng = (lng2 - lng1) * 111 * math.cos(math.radians(lat1))
    return math.sqrt(dlat**2 + dlng**2)

def calculate_real_seuil(lat, lng, current_seuil):
    dist = min(distance_km(lat, lng, p[0], p[1]) for p in GARONNE_POINTS)
    
    # On passe à 700 mètres pour le Seuil 1 (les quais + la première rue)
    if dist < 0.70: 
        return 1
        
    # On passe à 1.2 km pour le Seuil 2 (le centre historique)
    if dist < 1.20: 
        return 2
    
    return current_seuil
# --- EXÉCUTION ---
if not os.path.exists(SOURCE):
    print(f"❌ Erreur : {SOURCE} introuvable dans le dossier data.")
else:
    rows = []
    # On lit le fichier actuel
    with open(SOURCE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter="|")
        for row in reader:
            try:
                lat = float(row['lat'])
                lng = float(row['lng'])
                old_seuil = int(row['seuil'])
                
                # On applique la nouvelle logique de distance
                row['seuil'] = calculate_real_seuil(lat, lng, old_seuil)
                rows.append(row)
            except (ValueError, KeyError):
                rows.append(row) # Garde la ligne telle quelle si erreur

    # On écrase le fichier avec les nouveaux seuils
    with open(DESTINATION, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter="|")
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"✅ SUCCÈS : {len(rows)} établissements mis à jour avec les seuils 'Large'.")
    print(f"👉 Relance ton app.py et fais un rafraîchissement forcé (CMD+SHIFT+R).")