from app import db

# Modèle pour les utilisateurs
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    # Relation avec Project_detail
    project_details = db.relationship('Project_detail', back_populates='user')  # Pas de conflit

# Modèle pour les produits
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    version = db.Column(db.String(250), nullable=False)
    price = db.Column(db.Float, nullable=False)

    # Relation avec Project (many-to-many via ProjectProduct)
    projects = db.relationship('Project', secondary='project_products', back_populates='products')

    # Relation avec Product_state (one-to-one ou one-to-many)
    product_states = db.relationship('Product_state', back_populates='product')

# Modèle pour les projets
class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(250), nullable=True)

    # Relation avec Product (many-to-many via ProjectProduct)
    products = db.relationship('Product', secondary='project_products', back_populates='projects')

    # Relation avec Project_detail
    project_details = db.relationship('Project_detail', back_populates='project')

# Table d'association many-to-many entre Projects et Products
class ProjectProduct(db.Model):
    __tablename__ = 'project_products'
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)

# Modèle pour les détails d'un projet (lien entre un projet et un utilisateur)
class Project_detail(db.Model):
    __tablename__ = 'project_details'
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, primary_key=True)
    date_echeance = db.Column(db.DateTime, nullable=False)
    evolution_state = db.Column(db.Float, nullable=False)

    # Relations inverses
    project = db.relationship('Project', back_populates='project_details')
    user = db.relationship('User', back_populates='project_details')

# Modèle pour l'état d'un produit
class Product_state(db.Model):
    __tablename__ = 'product_states'
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, primary_key=True)
    stock = db.Column(db.Integer, nullable=True)
    destroy = db.Column(db.Integer, nullable=True)
    deffective = db.Column(db.Float, nullable=True)
    Addresse = db.Column(db.String(250), nullable=True)

    # Relation inversée avec Product
    product = db.relationship('Product', back_populates='product_states')
