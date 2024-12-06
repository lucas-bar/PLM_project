from . import db

# Modèle pour les utilisateurs
class User(db.Model):
    __tablename__ = 'users'  # Ajout du nom de la table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

