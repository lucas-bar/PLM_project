from app import db

# Modèle pour les utilisateurs
class User(db.Model):
    __tablename__ = 'users'  # Ajout du nom de la table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    products = db.relationship('UserProduct', backref='user', lazy=True)

# Modèle pour les projets
class Project(db.Model):
    __tablename__ = 'projects'  # Ajout du nom de la table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    
    # Relations avec les utilisateurs et produits
    users = db.relationship('UserProduct', backref='project', lazy=True)
    products = db.relationship('Product', backref='project', lazy=True)

# Modèle pour les produits
class Product(db.Model):
    __tablename__ = 'products'  # Ajout du nom de la table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    version = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    
    # Relation avec UserProduct
    users = db.relationship('UserProduct', backref='product', lazy=True)

# Modèle pour la relation utilisateur-produit
class UserProduct(db.Model):
    __tablename__ = 'user_products'  # Ajout du nom de la table
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Assurez-vous que le nom correspond à la table User
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  # Assurez-vous que le nom correspond à la table Product
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)  # Assurez-vous que le nom correspond à la table Project
    role = db.Column(db.String(50), nullable=False)

