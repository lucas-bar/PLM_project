from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Product, UserProduct

# Créer un blueprint pour les routes
bp = Blueprint('routes', __name__)

# Route pour l'enregistrement d'un utilisateur
@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Utilisateur créé avec succès."}), 201

# Route pour la connexion d'un utilisateur
@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        return jsonify({"message": "Connexion réussie."}), 200
    return jsonify({"message": "Nom d'utilisateur ou mot de passe incorrect."}), 401

# Route pour ajouter un produit
@bp.route('/products', methods=['POST'])
def add_product():
    data = request.json
    new_product = Product(name=data['name'], description=data['description'], version=data['version'], stock=data['stock'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Produit ajouté avec succès."}), 201

# Route pour obtenir tous les produits
@bp.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{"id": p.id, "name": p.name, "description": p.description, "version": p.version, "stock": p.stock} for p in products]), 200

# Route pour assigner un utilisateur à un produit
@bp.route('/assign_user', methods=['POST'])
def assign_user():
    data = request.json
    user_product = UserProduct(user_id=data['user_id'], product_id=data['product_id'], role=data['role'])
    db.session.add(user_product)
    db.session.commit()
    return jsonify({"message": "Utilisateur assigné au produit avec succès."}), 201

# Route pour obtenir les détails d'un produit
@bp.route('/products/details', methods=['GET'])
def product_details():
    product_id = request.args.get('id')
    product = Product.query.get(product_id)

    if not product:
        return jsonify({"message": "Produit non trouvé."}), 404

    return jsonify({
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "stock": product.stock,
        "version": product.version,
        "users": [{"id": user.id, "username": user.username} for user in product.users]
    }), 200

# Assurez-vous de lier le blueprint à l'application
def register_routes(app):
    app.register_blueprint(bp, url_prefix='/api')
