from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, session
from app import db
from app.models import User, Ingredient, Product, Product_detail, product_ingredients, Comment, Usine, Production
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from datetime import datetime

bp = Blueprint('routes', __name__)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@bp.route('/acceuil', methods=['GET', 'POST'])
def acceuil():
    return render_template('acceuil.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id  
            session['username'] = user.username
            session['user_poste'] = user.poste
            flash('You have been successfully logged in!', 'success')
            if session['user_poste'] == 1:
                return redirect(url_for('routes.dashboard'))
            else:
                return redirect(url_for('routes.afficher_usines'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Vous êtes déconnecté.", "success")
    return redirect(url_for('routes.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        poste = request.form['poste']
        if poste == "production":
            poste = 0
        else:
            poste = 1
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists!', 'danger')
            return redirect(url_for('routes.register'))
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password, poste=poste)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('routes.login'))
    return render_template('register.html')

@bp.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('routes.login')) 
    username = session['username']  # Récupérer le nom d'utilisateur depuis la session
    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect(url_for('routes.login'))  
    ingredients = Ingredient.query.all()
    produits = (db.session.query(Product).join(Product_detail, Product.id == Product_detail.product_id).filter(Product_detail.username == username).all())
    for produit in produits:
        produit.details = Product_detail.query.filter_by(product_id=produit.id).first()
    return render_template('dashboard.html', user=user, produits=produits, ingredients=ingredients)

@bp.route('/ingredients')
def afficher_ingredients():
    if 'user_id' not in session:
        return redirect(url_for('routes.login')) 
    user_id = session['user_id']
    user = User.query.get(user_id)  
    if not user:
        return redirect(url_for('routes.login'))  
    ingredients = Ingredient.query.all()
    return render_template('ingredients.html', user=user, ingredients=ingredients)

@bp.route('/produits')
def afficher_produits():
    if 'user_id' not in session:
        return redirect(url_for('routes.login')) 
    username = session['username']  # Récupérer le nom d'utilisateur depuis la session
    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect(url_for('routes.login'))  
    produits = (
        db.session.query(Product)
        .join(Product_detail, Product.id == Product_detail.product_id)
        .filter(Product_detail.username == username)
        .all()
    )
    return render_template('produits.html', user=user, produits=produits)

@bp.route('/ajouter-ingredient', methods=['GET', 'POST'])
def ajouter_ingredient():
    if request.method == 'POST':
        nom = request.form.get('nom')
        prix = request.form.get('prix')
        quantite = request.form.get('quantite')
        if not nom or not prix or not quantite:
            flash('Tous les champs sont obligatoires.', 'error')
            return redirect(url_for('routes.ajouter_produit'))
        try:
            prix = float(prix)
            quantite = int(quantite)
            new_ingredient = Ingredient(name=nom, price=prix, quantity=quantite)
            db.session.add(new_ingredient)
            db.session.commit()
            flash('Produit ajouté avec succès.', 'success')
            return redirect(url_for('routes.afficher_ingredients'))
        except ValueError:
            flash('Le prix doit être un nombre décimal et la quantité un entier.', 'error')
    return render_template('ajouter_ingredient.html')

@bp.route('/ajouter-produit', methods=['GET', 'POST'])
def ajouter_produit():
    if request.method == 'POST':
        nom_produit = request.form.get('name')
        gamme = request.form.get('gamme')
        date_echeance = request.form.get('date_echeance')
        evolution_state = 0
        etat = 0
        username = session.get('username')
        print(username)
        ingredient_ids = request.form.getlist('ingredients')
        if not nom_produit or not gamme or not date_echeance or not username:
            return render_template('ajouter_produit.html')
        try:
            date_echeance = datetime.strptime(date_echeance, '%Y-%m-%d')
            username = str(username)
            nouveau_produit = Product(name=nom_produit)
            db.session.add(nouveau_produit)
            db.session.commit()
            nouveau_detail = Product_detail(product_id=nouveau_produit.id, username=username, gamme=gamme, date_echeance=date_echeance, evolution_state=evolution_state, etat=etat)
            db.session.add(nouveau_detail)
            db.session.commit()
            for ingredient_id in ingredient_ids:
                ingredient = Ingredient.query.get(ingredient_id)
                if ingredient:
                    product_ingredient = Product_Ingredient(id_product=nouveau_produit.id, name_product=nouveau_produit.name, id_ingredient=ingredient.id, name_ingredient=ingredient.name)
                    db.session.add(product_ingredient)
            flash("Produit et détails ajoutés avec succès !", "success")
            return redirect(url_for('routes.afficher_produits'))
        except Exception as e:
            logger.debug(f"Erreur lors de l'ajout : {str(e)}", "error")
            flash(f"Erreur lors de l'ajout : {str(e)}", "error")
            return redirect(url_for('routes.afficher_produits'))
    ingredients = Ingredient.query.all()
    return render_template('ajouter_produit.html', ingredients=ingredients)

@bp.route('/modifier-ingredient/<int:ingredient_id>', methods=['GET', 'POST'])
def modifier_ingredient(ingredient_id):
    ingredient = Ingredient.query.get(ingredient_id)
    if request.method == 'POST':
        ingredient.name = request.form['name']
        ingredient.price = request.form['price']
        ingredient.quantity = request.form['quantity']
        db.session.commit()
        return redirect(url_for('routes.afficher_ingredients'))
    return render_template('modifier_ingredient.html', ingredient=ingredient)

@bp.route('/modifier-produit/<int:produit_id>', methods=['GET', 'POST'])
def modifier_produit(produit_id):
    produit = Product.query.get(produit_id)
    produit_detail = Product_detail.query.filter_by(product_id=produit_id).first()
    comments = Comment.query.filter_by(product_id=produit_id).order_by(Comment.timestamp.desc()).all()

    if not produit or not produit_detail:
        flash("Produit introuvable.", "error")
        return redirect(url_for('routes.dashboard'))

    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            nom_produit = request.form.get('name')
            gamme = request.form.get('gamme')
            date_echeance = request.form.get('date_echeance')
            username = request.form.get('username')
            ingredient_ids = request.form.getlist('ingredients')
            evolution_state = request.form.get('evolution_state')
            comment_text = request.form.get('comments')  # Récupérer le commentaire
            usine_emballage = request.form.get('usine_emballage')
            usine_embouteillage = request.form.get('usine_embouteillage')
            usine_melange = request.form.get('usine_melange')
            usine_filtration = request.form.get('usine_filtration')
            usine_maturation = request.form.get('usine_maturation')
            usine_extraction = request.form.get('usine_extraction')

            # Validation des champs obligatoires
            if not nom_produit or not gamme or not date_echeance or not username:
                flash("Tous les champs obligatoires doivent être remplis.", "error")
                return redirect(url_for('routes.modifier_produit', produit_id=produit_id))

            # Validation de `evolution_state`
            try:
                produit_detail.evolution_state = float(evolution_state)
                if not (0 <= produit_detail.evolution_state <= 100):
                    raise ValueError("La valeur d'avancement doit être comprise entre 0 et 100.")
            except ValueError:
                flash("La valeur d'avancement doit être un nombre valide compris entre 0 et 100.", "error")
                return redirect(url_for('routes.modifier_produit', produit_id=produit_id))

            # Mettre à jour les informations du produit
            produit.name = nom_produit
            produit_detail.gamme = gamme
            produit_detail.date_echeance = datetime.strptime(date_echeance, '%Y-%m-%d')
            produit_detail.username = username

            # Mettre à jour les usines sélectionnées
            produit_detail.usine_emballage = usine_emballage
            produit_detail.usine_embouteillage = usine_embouteillage
            produit_detail.usine_melange = usine_melange
            produit_detail.usine_filtration = usine_filtration
            produit_detail.usine_maturation = usine_maturation
            produit_detail.usine_extraction = usine_extraction

            # Mettre à jour les ingrédients associés
            db.session.execute(
                product_ingredients.delete().where(product_ingredients.c.id_product == produit_id)
            )
            for ingredient_id in ingredient_ids:
                ingredient = Ingredient.query.get(ingredient_id)
                if ingredient:
                    db.session.execute(
                        product_ingredients.insert().values(
                            id_product=produit.id,
                            name_product=produit.name,
                            id_ingredient=ingredient.id,
                            name_ingredient=ingredient.name
                        )
                    )

            # Enregistrer le commentaire s'il existe
            if comment_text:
                new_comment = Comment(
                    product_id=produit.id,
                    username=username,
                    text=comment_text,
                    timestamp=datetime.utcnow()
                )
                db.session.add(new_comment)

            db.session.commit()  # Effectuer un seul commit pour toutes les modifications

            flash("Produit modifié avec succès !", "success")
            return redirect(url_for('routes.afficher_produits'))
        except Exception as e:
            logger.debug(f"Erreur lors de la modification : {str(e)}")
            flash(f"Erreur lors de la modification : {str(e)}", "error")
            return redirect(url_for('routes.modifier_produit', produit_id=produit_id))

    # Charger les usines par type pour le formulaire
    usines_emballage = Usine.query.filter(Usine.types == 'Emballage').all()
    usines_embouteillage = Usine.query.filter(Usine.types == 'Embouteillage').all()
    usines_melange = Usine.query.filter(Usine.types == 'Mélange').all()
    usines_filtration = Usine.query.filter(Usine.types == 'Filtration').all()
    usines_maturation = Usine.query.filter(Usine.types == 'Maturation').all()
    usines_extraction = Usine.query.filter(Usine.types == 'Extraction de matières premières').all()

    # Charger les ingrédients pour le formulaire
    ingredients = Ingredient.query.all()
    selected_ingredients = [
        row.id_ingredient
        for row in db.session.execute(
            db.select(product_ingredients.c.id_ingredient).where(product_ingredients.c.id_product == produit_id)
        )
    ]

    return render_template(
        'modifier_produit.html',
        produit=produit,
        produit_detail=produit_detail,
        ingredients=ingredients,
        selected_ingredients=selected_ingredients,
        comments=comments,
        usines_emballage=usines_emballage,
        usines_embouteillage=usines_embouteillage,
        usines_melange=usines_melange,
        usines_filtration=usines_filtration,
        usines_maturation=usines_maturation,
        usines_extraction=usines_extraction
    )


@bp.route('/supprimer-ingredient/<int:ingredient_id>', methods=['GET', 'POST'])
def supprimer_ingredient(ingredient_id):
    try:
        ingredient = Ingredient.query.get(ingredient_id)
        if not ingredient:
            flash("Ingrédient introuvable.", "error")
            return redirect(url_for('routes.dashboard'))  
        db.session.delete(ingredient)
        db.session.commit()
        flash(f"L'ingrédient '{ingredient.name}' a été supprimé avec succès.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Une erreur est survenue lors de la suppression : {str(e)}", "error")
    return redirect(url_for('routes.afficher_ingredients'))


@bp.route('/supprimer-produit/<int:produit_id>', methods=['GET', 'POST'])
def supprimer_produit(produit_id):
    try:
        produit = Product.query.get(produit_id)
        if not produit:
            flash("Produit introuvable.", "error")
            return redirect(url_for('routes.dashboard'))  
        db.session.delete(produit)
        db.session.commit()
        flash(f"Le produit '{produit.name}' a été supprimé avec succès.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Une erreur est survenue lors de la suppression : {str(e)}", "error")
    return redirect(url_for('routes.afficher_produits'))

@bp.route('/usines')
def afficher_usines():
    if 'user_id' not in session:
        return redirect(url_for('routes.login')) 
    user_id = session['user_id']
    user = User.query.get(user_id) 
    if not user:
        return redirect(url_for('routes.login'))  

    # Récupérer toutes les usines
    usines = Usine.query.all()  

    # Récupérer les produits avec un avancement de 100 et un état de 0
    produits = (db.session.query(Product)
                .join(Product_detail)
                .filter(Product_detail.evolution_state == 100, Product_detail.etat == 0)
                .all())

    return render_template(
        'production.html',
        user=user,
        usines=usines,
        produits=produits
    )


@bp.route('/ajouter-usine', methods=['GET', 'POST'])
def ajouter_usine():
    if request.method == 'POST':
        pays = request.form.get('pays')
        types = request.form.get('types')
        
        if not pays or not types:
            flash('Tous les champs sont obligatoires.', 'error')
            return redirect(url_for('routes.ajouter_usine'))
        
        new_usine = Usine(pays=pays, types=types)
        db.session.add(new_usine)
        db.session.commit()
        
        flash('Usine ajoutée avec succès.', 'success')
        return redirect(url_for('routes.afficher_usines'))
    
    return render_template('ajouter_usine.html')

@bp.route('/lancer-production/<int:product_id>', methods=['POST'])
def lancer_production(product_id):
    data = request.get_json()
    quantity = data.get('quantity')
    etat = data.get('etat')

    if not quantity or not etat:
        return jsonify({"success": False, "message": "Quantité et état sont requis."}), 400

    try:
        # Trouver le produit dans la base de données
        product = Product.query.get(product_id)

        if not product:
            return jsonify({"success": False, "message": "Produit non trouvé."}), 404

        # Récupérer l'usine de matières premières associée au produit
        usine = Usine.query.get(product.usine_id)  # Assurez-vous que `usine_id` est la relation correcte

        if not usine:
            return jsonify({"success": False, "message": "Usine de matières premières non trouvée."}), 404

        # Trouver ou créer une production pour ce produit
        production = Production.query.filter_by(product_id=product_id).first()

        if not production:
            # Si aucune production n'existe pour ce produit, on en crée une nouvelle
            production = Production(
                product_id=product_id,
                usines_id=usine.id,  # L'ID de l'usine est celui de l'usine de matières premières
                aprod=quantity,      # La quantité à produire est enregistrée dans aprod
                prod=0,              # Commence à 0
                defect=0             # On suppose qu'il n'y a pas de défaut au début
            )
            db.session.add(production)
        else:
            # Si une production existe déjà, on met à jour la quantité à produire
            production.aprod += quantity  # Ajoute la quantité à la production actuelle

        # Trouver ou créer un détail de produit pour ce produit
        product_detail = Product_detail.query.filter_by(product_id=product_id).first()

        if not product_detail:
            # Si aucun détail de produit n'existe, on en crée un nouveau
            product_detail = Product_detail(
                product_id=product_id,
                etat=1  # Initialiser l'état à 1 lors du lancement de la production
            )
            db.session.add(product_detail)
        else:
            # Mettre à jour l'état si un détail de produit existe déjà
            product_detail.etat = 1

        # Mettre à jour l'état du produit (facultatif, selon vos besoins)
        product.etat = etat
        db.session.commit()

        return jsonify({"success": True, "message": "Production lancée avec succès."})

    except Exception as e:
        db.session.rollback()  # En cas d'erreur, on annule les changements
        return jsonify({"success": False, "message": f"Erreur lors du lancement de la production: {str(e)}"}), 500






def register_routes(app):
    app.register_blueprint(bp)