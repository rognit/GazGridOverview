# GazGridOverview

GazGridOverview est un projet visant à fournir une interface interactive permettant le visionnage des tronçons survolables du réseau de gaz de la France métropolitaine (GRTgaz + Teréga). Ce projet est conçu pour offrir une visualisation claire et intuitive des infrastructures de gaz, facilitant ainsi la surveillance du réseau par voie aérienne.

## Fonctionnalités

- **Visualisation Interactive** : Interface utilisateur permettant de naviguer facilement à travers le réseau de gaz français.
- **Survol des Tronçons** : Possibilité de survoler et de zoomer sur les différentes sections du réseau.
- **Informations Détaillées** : Affichage d'informations détaillées sur chaque tronçon du réseau.
- **Cartographie Dynamique** : Utilisation de cartes interactives pour une meilleure compréhension des données géographiques.


## Installation

Clonez le dépôt et installez les dépendances :

```bash
git clone https://github.com/votre-utilisateur/GazGridOverview.git
cd GazGridOverview
pip install -r requirements.txt
```








```bash
pyinstaller --onefile --windowed --add-data 'resources/gaz_network.csv:resources' --add-data 'resources/gaz_network_colored.csv:resources' --add-data 'resources/gaz_network_colored_merged.csv:resources' --add-data 'resources/pop_filtered.csv:resources' --name GazGridOverview main.py
```