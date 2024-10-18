from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Product, UserProduct, Project  


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
    
# Route pour créer un projet
@bp.route('/projects', methods=['POST'])
def create_project():
    data = request.json
    new_project = Project(name=data['name'], description=data['description'])
    db.session.add(new_project)
    db.session.commit()
    return jsonify({"message": "Projet créé avec succès.", "project_id": new_project.id}), 201

# Route pour ajouter un produit à un projet
@bp.route('/projects/<int:project_id>/products', methods=['POST'])
def add_product_to_project(project_id):
    data = request.json
    product = Product(name=data['name'], description=data['description'], version=data['version'], stock=data['stock'], project_id=project_id)
    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "Produit ajouté au projet."}), 201

# Route pour supprimer un produit d'un projet
@bp.route('/projects/<int:project_id>/products/<int:product_id>', methods=['DELETE'])
def remove_product_from_project(project_id, product_id):
    product = Product.query.filter_by(id=product_id, project_id=project_id).first()
    if not product:
        return jsonify({"message": "Produit non trouvé."}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Produit supprimé du projet."}), 200

# Route pour affecter un utilisateur à un produit dans un projet
@bp.route('/projects/<int:project_id>/assign_user', methods=['POST'])
def assign_user_to_product(project_id):
    data = request.json
    user_product = UserProduct(user_id=data['user_id'], product_id=data['product_id'], project_id=project_id, role=data['role'])
    db.session.add(user_product)
    db.session.commit()
    return jsonify({"message": "Utilisateur assigné au produit avec succès."}), 201

@bp.route('/dashboard', methods=['GET'])
def dashboard():
    projects = Project.query.all()
    dashboard_data = {
        "projects": [],
        "total_products": 0,
        "total_stock": 0,
    }
    
    for project in projects:
        project_data = {
            "id": project.id,
            "name": project.name,
            "total_products": len(project.products),
            "total_stock": sum([p.stock for p in project.products]),
        }
        dashboard_data["projects"].append(project_data)
        dashboard_data["total_products"] += project_data["total_products"]
        dashboard_data["total_stock"] += project_data["total_stock"]

    return jsonify(dashboard_data), 200

@bp.route('/products/search', methods=['GET'])
def search_products():
    status = request.args.get('status')
    if status not in ['fabriqué', 'en stock', 'détruit', 'défectueux', 'livré']:
        return jsonify({"message": "Statut non valide."}), 400
    
    # Remplacer par votre logique de filtrage de produits
    # C'est un exemple, vous devez adapter la logique en fonction de votre base de données.
    products = Product.query.filter_by(status=status).all()  # Exemple de recherche
    return jsonify([{"id": p.id, "name": p.name} for p in products]), 200


@bp.route('/products/details/<int:product_id>', methods=['GET'])
def product_detail(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Produit non trouvé."}), 404
    
    return jsonify({
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "stock": product.stock,
        "version": product.version,
    }), 200

@bp.route('/suggestions', methods=['POST'])
def suggest_perfume():
    data = request.json
    characteristics = data.get('characteristics', [])
    
    # Remplacez ceci par votre logique de suggestion
    suggestions = []  # Remplissez avec des suggestions basées sur les caractéristiques
    return jsonify({"suggestions": suggestions}), 200

