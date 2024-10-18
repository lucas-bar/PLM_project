from app import db

# Modèle pour les utilisateurs
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    products = db.relationship('UserProduct', backref='user', lazy=True)

# Modèle pour les produits
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    version = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    users = db.relationship('UserProduct', backref='product', lazy=True)

# Modèle pour la relation utilisateur-produit
class UserProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)
