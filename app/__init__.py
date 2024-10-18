# app/__init__.py

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modèle pour les utilisateurs
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Route pour la connexion
@app.route('/login', methods=['POST'])
def login():
    # Récupérer les données JSON envoyées
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    # Vérifiez si l'utilisateur existe
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password, password):
        # Authentification réussie
        return jsonify({"message": "Connexion réussie!"}), 200
    else:
        # Authentification échouée
        return jsonify({"message": "Nom d'utilisateur ou mot de passe incorrect."}), 401
    
# Fonction pour ajouter un nouvel utilisateur
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Vérifiez si l'utilisateur existe déjà
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Nom d'utilisateur déjà pris."}), 400

    # Hachage du mot de passe
    hashed_password = generate_password_hash(password, method='sha256')

    # Créer un nouvel utilisateur
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Utilisateur créé avec succès!"}), 201


if __name__ == '__main__':
    app.run(debug=True)
