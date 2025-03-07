# commande_internet
Projet réaliser par le groupe : 
Jonathan GUIL - GUIJ24090400
Tom JAMMES - JAMT27100400
Constant Nguyen  - NGUC31080400
Gabriel SAUVAGNAC - SAUG06120400


## 1. Cloner le projet : 

``git clone https://github.com/GabrielSau/commande_internet.git``

## 2. Créer l'environnement virtuel :

``python -m venv venv``

``.\venv\Scripts\Activate``

``pip install -r requirements.txt``

## 3. Initialisation de la base de données :

``$env:FLASK_APP="inf349.py"``

``flask init-db``

## 4. Lancer l'application :

``flask run``

L'application est disponible sur : http://localhost:5000

## 5. Desactiver l'environnement virtuel

``deactivate``


## 6. Pour les tests : 

``pip install pytest pytest-flask``

``pytest``


