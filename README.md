# commande_internet
1. Cloner le projet : 
git clone https://github.com/ton-repo/commande_internet.git

2. Créer l'environnement virtuel :
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt

3. Initialisation de la base de données :
$env:FLASK_APP = "inf349.py"
flask init-db

4. Lancer l'application :
flask run

L'application est disponible sur : http://localhost:5000


Pour les tests : 
pip install pytest pytest-flask
pytest


