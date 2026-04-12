# 🌊 Bordeaux SafeSim

> **Une plateforme interactive d'anticipation et de gestion des crises climatiques pour la métropole bordelaise.**

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0.0-lightgrey?style=flat-square&logo=flask)
![Pandas](https://img.shields.io/badge/Pandas-2.1.1-150458?style=flat-square&logo=pandas)
![Geopandas](https://img.shields.io/badge/Geopandas-Data_Science-brightgreen?style=flat-square)
![Hackathon](https://img.shields.io/badge/Hackathon-Holberton_School_x_Bordeaux_M%C3%A9tropole-ff69b4?style=flat-square)

---

## 🏆 Contexte du Projet

Ce projet a été développé dans le cadre du **Hackathon organisé par Holberton School en collaboration avec Bordeaux Métropole**. 
L'objectif central était d'exploiter les données ouvertes (Open Data) générées par la métropole pour créer une solution innovante répondant aux enjeux de la **résilience climatique**.

Face à l'urgence environnementale, l'anticipation est notre bouclier le plus précieux. **Bordeaux SafeSim** permet de visualiser les risques climatiques de manière accessible et interactive, offrant ainsi une "vigie numérique" pour les citoyens comme pour les décideurs locaux.

## ✨ Fonctionnalités Principales

Le projet se décompose en deux modules majeurs d'analyse et de visualisation :

*   **💧 Simulateur de Crue (War Room)** : 
    *   Simulation interactive de la montée des eaux (niveaux ajustables).
    *   Croisement des données altimétriques et des seuils critiques des ERP (Établissements Recevant du Public).
    *   Suivi en direct de l'impact sur les infrastructures critiques (Hôpitaux, Écoles, Mairies, EHPAD).
    *   Indicateurs globaux d'impact sur la capacité de la ville.
*   **🌡️ Cartographie des Îlots de Chaleur** : 
    *   Visualisation spatiale des zones de surchauffe urbaine (ICU) via des données GeoJSON.
    *   Identification des zones de vulnérabilité thermique lors des canicules pour adapter l'aménagement urbain.

## 🛠️ Stack Technique

*   **Backend** : Python 3.11, Flask
*   **Data Science & Géospatial** : Pandas, Geopandas, NumPy, SciPy, Shapely, PyProj
*   **Serveur de Production** : Gunicorn
*   **Frontend** : HTML5, CSS3, JavaScript (Leaflet.js pour la cartographie)

## 📊 Données Utilisées (Open Data)

Bordeaux SafeSim exploite des données massives pour ses simulations :
*   `bor_erp_managed.csv` : Données sur les *Établissements Recevant du Public*, incluant leurs capacités, leurs types, leurs altitudes et les statuts PPRI.
*   `ri_icu_ifu_s.geojson` : Relevés géographiques et thermiques des îlots de chaleur sur le territoire.

## 🚀 Installation & Exécution locale

### Prérequis
Assurez-vous d'avoir [Python 3.11+](https://www.python.org/) d'installé sur votre machine.

### Étapes

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/loties1533/bordeaux-safesim.git
   cd bordeaux-safesim
   ```

2. **Créer un environnement virtuel (recommandé)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Mac/Linux
   venv\Scripts\activate     # Sur Windows
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Lancer l'application en mode développement**
   ```bash
   python app.py
   ```
   *L'application sera accessible sur `http://127.0.0.1:5000`.*

## 🌐 Déploiement

Cette application est configurée pour être facilement déployable sur des plateformes PaaS comme **Render** ou **Heroku**.
*   **Dépendances prêtes** : Le fichier `requirements.txt` intègre `gunicorn` pour le serveur de production.
*   **Procfile** : Présent à la racine pour indiquer la commande de démarrage (`web: gunicorn app:app`).
*   *Note pour Render : Veillez à spécifier la variable d'environnement `PYTHON_VERSION=3.11.9` pour assurer la compatibilité logicielle de Geopandas/Pandas.*

---
*Fait avec ❤️ pour Holberton School & Bordeaux Métropole*
