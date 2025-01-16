from app import db
from sqlalchemy import Enum
from datetime import datetime
from sqlalchemy.orm import foreign


# Table secondaire pour les relations many-to-many
product_ingredients = db.Table(
    'product_ingredients',
    db.Column('id_product', db.Integer, db.ForeignKey('products.id'), primary_key=True),
    db.Column('name_product', db.String(100), nullable=False),
    db.Column('id_ingredient', db.Integer, db.ForeignKey('ingredients.id'), primary_key=True),
    db.Column('name_ingredient', db.String(100), nullable=False)
)

# Modèle User
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    poste = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    product_details = db.relationship('Product_detail', back_populates='user')

# Modèle Ingredient
class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    products = db.relationship('Product', secondary=product_ingredients, back_populates='ingredients')
    product_states = db.relationship('Product_state', back_populates='product')

# Modèle Product
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    product_details = db.relationship('Product_detail', back_populates='project')
    ingredients = db.relationship('Ingredient', secondary=product_ingredients, back_populates='products')

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    username = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Modèle Product_detail
class Product_detail(db.Model):
    __tablename__ = 'product_details'
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, primary_key=True)
    username = db.Column(db.String, db.ForeignKey('users.username'), nullable=False, primary_key=True)
    gamme = db.Column(Enum('masculin', 'feminin', 'mixte', name='gamme_enum'), nullable=False, default='mixte')
    date_echeance = db.Column(db.DateTime, nullable=False)
    evolution_state = db.Column(db.Float, nullable=False)
    project = db.relationship('Product', back_populates='product_details')
    user = db.relationship('User', back_populates='product_details')
    
# Modèle Product_state
class Product_state(db.Model):
    __tablename__ = 'product_states'
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False, primary_key=True)
    stock = db.Column(db.Integer, nullable=True)
    destroy = db.Column(db.Integer, nullable=True)
    deffective = db.Column(db.Float, nullable=True)
    address = db.Column(db.String(250), nullable=True)
    product = db.relationship('Ingredient', back_populates='product_states')

