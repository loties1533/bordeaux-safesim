# 🌊 BORDEAUX | SAFE-SIM
SAFE-SIM est une plateforme de simulation de crise en temps réel permettant de visualiser l'impact d'une crue de la Garonne sur les Établissements Recevant du Public (ERP) de Bordeaux Métropole.

## 🚀 Concept
L'application croise les données géographiques des ERP avec un Modèle Numérique de Terrain (MNT) pour simuler, via un curseur dynamique, la montée des eaux. Elle permet d'identifier instantanément les zones critiques et d'évaluer la capacité d'accueil/survie impactée.

## 🛠 Stack Technique
Backend : Python 3.x avec Flask (API REST et service des templates).

Data Analysis : Pandas pour le traitement et le filtrage des données géospatiales.

Frontend : * Leaflet.js pour la cartographie haute performance (rendu Canvas).

Tailwind CSS pour l'interface utilisateur type "War Room".

Share Tech Mono (Google Fonts) pour l'esthétique technique.

Data Enhancement : Intégration prévue de l'API Altimétrie de l'IGN pour le calcul des seuils critiques.

## 📂 Structure du Projet

```Plaintext
bordeaux-safesim/
├── app.py              # Serveur Flask et logique API
├── requirements.txt    # Dépendances Python
├── templates/          # Vues HTML (index.html)
├── static/             # Assets (CSS personnalisé, JS moteur de carte)
│   ├── styles.css      # Design et animations pulse
│   ├── map.js          # Moteur Cartographique (Leaflet + Canvas)
│   └── simulator.js    # Gestion des événements slider et appels API
└── data/
    └── processed/      # Données ERP enrichies (Z/Altitude)
```

## ⚙️ Installation et Lancement
Cloner le dépôt :

```Bash
git clone https://github.com/loties1533/bordeaux-safesim
cd bordeaux-safesim
```

Installer les dépendances :

```Bash
pip install -r requirements.txt
```

Lancer l'application :

```Bash
python app.py
```

L'interface est alors accessible sur http://127.0.0.1:5000.

## 📈 Fonctionnalités
Simulation Dynamique : Slider de 0m à 7m (NGF) avec mise à jour des marqueurs sans rafraîchissement de page.

Performance : Utilisation du rendu Canvas de Leaflet permettant d'afficher plus de 8 000 points de manière fluide.

Analyse d'Impact : Calcul en temps réel du nombre de personnes impactées et du pourcentage de survie de la ville.

Interface Responsive : Panneau de contrôle escamotable et mode de carte commutable (Dark/Light).

## 👥 Équipe (Hackathon 2026)
Axel (Data) : Nettoyage, enrichissement altimétrique via LiDAR/IGN.

Alexis (Backend) : Logique de simulation et API Flask.

Antoine (Carto/JS) : Intégration Leaflet, performance Canvas et logique frontend.

Anil (UI/UX) : Design système, Tailwind CSS et animations.

Projet réalisé dans le cadre de la gestion des risques inondation de Bordeaux Métropole.