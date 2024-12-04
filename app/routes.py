from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Product, Project,  ProjectProduct, Project_detail  # Ajout des tables de jointure
from datetime import datetime

# Créer un blueprint pour les routes
bp = Blueprint('routes', __name__)

def register_routes(app):
    app.register_blueprint(bp)
    
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
    new_product = Product(
        name=data['name'],
        description=data['description'],
        version=data['version'],
        price=data['price']  # Le prix est maintenant un champ dans le modèle Product
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Produit ajouté avec succès."}), 201

# Route pour obtenir tous les produits
@bp.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "version": p.version,
        "price": p.price  # Affichage du prix des produits
    } for p in products]), 200


@bp.route('/projects', methods=['POST'])
def add_project():
    data = request.json
    try:
        # Crée un nouveau projet
        new_project = Project(
            name=data['name'],
            description=data.get('description', None)  # `description` est facultatif
        )
        db.session.add(new_project)
        db.session.commit()
        return jsonify({"message": "Projet ajouté avec succès.", "project_id": new_project.id}), 201
    except KeyError:
        return jsonify({"message": "Données invalides. Veuillez inclure 'name' dans la requête."}), 400
    except Exception as e:
        return jsonify({"message": f"Erreur lors de l'ajout du projet : {str(e)}"}), 500

@bp.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    try:
        # Recherche du projet
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"message": "Projet non trouvé."}), 404

        # Supprime le projet
        db.session.delete(project)
        db.session.commit()
        return jsonify({"message": "Projet supprimé avec succès."}), 200
    except Exception as e:
        return jsonify({"message": f"Erreur lors de la suppression du projet : {str(e)}"}), 500
    
@bp.route('/projects', methods=['GET'])
def get_projects():
    try:
        projects = Project.query.all()
        return jsonify([
            {"id": project.id, "name": project.name, "description": project.description}
            for project in projects
        ]), 200
    except Exception as e:
        return jsonify({"message": f"Erreur lors de la récupération des projets : {str(e)}"}), 500
    
    
# Route pour ajouter un produit à un projet
@bp.route('/projects/<int:project_id>/products', methods=['POST'])
def add_product_to_project(project_id):
    data = request.json
    product_ids = data.get('product_ids', [])  # Liste des ids des produits à associer au projet
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"message": "Projet non trouvé."}), 404
    
    # Lier les produits au projet via la table de jointure ProjectProduct
    for product_id in product_ids:
        product = Product.query.get(product_id)
        if product:
            new_association = ProjectProduct(project_id=project_id, product_id=product_id)
            db.session.add(new_association)
    
    db.session.commit()
    return jsonify({"message": "Produit(s) ajouté(s) au projet avec succès."}), 201

# Route pour supprimer un produit d'un projet
@bp.route('/projects/<int:project_id>/products/<int:product_id>', methods=['DELETE'])
def remove_product_from_project(project_id, product_id):
    product_project = ProjectProduct.query.filter_by(project_id=project_id, product_id=product_id).first()
    if not product_project:
        return jsonify({"message": "Produit non trouvé dans ce projet."}), 404
    db.session.delete(product_project)
    db.session.commit()
    return jsonify({"message": "Produit supprimé du projet avec succès."}), 200

# Route pour affecter un utilisateur à un projet (table Project_detail)
@bp.route('/projects/<int:project_id>/assign_user', methods=['POST'])
def assign_user_to_project(project_id):
    data = request.json

    # Vérification de l'existence du projet
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"message": "Projet non trouvé."}), 404

    # Vérification de l'existence de l'utilisateur
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({"message": "Utilisateur non trouvé."}), 404

    # Conversion de la date d'échéance en objet datetime
    try:
        date_echeance = datetime.strptime(data['date_echeance'], "%Y-%m-%d")  # Format attendu : "YYYY-MM-DD"
    except ValueError:
        return jsonify({"message": "Format de date non valide. Utilisez le format 'YYYY-MM-DD'."}), 400

    # Création d'une nouvelle entrée dans la table Project_detail
    new_project_detail = Project_detail(
        project_id=project_id,
        user_id=data['user_id'],
        date_echeance=date_echeance,
        evolution_state=data['evolution_state']  # Ex: 0.5 (50%)
    )

    db.session.add(new_project_detail)
    db.session.commit()
    return jsonify({"message": "Utilisateur assigné au projet avec succès."}), 201
# Route pour le dashboard
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
            "total_products": len(project.products),  # Nombre de produits associés au projet
            "total_stock": sum([p.stock for p in project.products]),  # Somme des stocks des produits
        }
        dashboard_data["projects"].append(project_data)
        dashboard_data["total_products"] += project_data["total_products"]
        dashboard_data["total_stock"] += project_data["total_stock"]

    return jsonify(dashboard_data), 200

# Route pour la recherche de produits
@bp.route('/products/search', methods=['GET'])
def search_products():
    status = request.args.get('status')
    if status not in ['fabriqué', 'en stock', 'détruit', 'défectueux', 'livré']:
        return jsonify({"message": "Statut non valide."}), 400
    
    # Exemple de recherche de produits par statut
    products = Product.query.filter_by(status=status).all()
    return jsonify([{"id": p.id, "name": p.name} for p in products]), 200

# Route pour obtenir les détails d'un produit
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

# Route pour les suggestions (exemple générique)
@bp.route('/suggestions', methods=['POST'])
def suggest_perfume():
    data = request.json
    characteristics = data.get('characteristics', [])
    
    # Remplacer ceci par votre logique de suggestion
    suggestions = []  # Remplissez avec des suggestions basées sur les caractéristiques
    return jsonify({"suggestions": suggestions}), 200
