from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, session
from app import db
from app.models import User, Ingredient, Product, Product_detail, product_ingredients, Comment
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
            flash('You have been successfully logged in!', 'success')
            return redirect(url_for('routes.dashboard'))
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
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists!', 'danger')
            return redirect(url_for('routes.register'))
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('routes.login'))
    return render_template('register.html')

@bp.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('routes.login')) 
    user_id = session['user_id']
    user = User.query.get(user_id)  
    if not user:
        return redirect(url_for('routes.login'))  
    ingredients = Ingredient.query.all()
    produits = Product.query.all() 
    for produit in produits:
        produit.details = Product_detail.query.filter_by(product_id=produit.id).first()
    return render_template('dashboard.html', user=user, produits=produits, ingredients=ingredients)

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
            return redirect(url_for('routes.dashboard'))
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
        username = request.form.get('username') 
        ingredient_ids = request.form.getlist('ingredients')
        if not nom_produit or not gamme or not date_echeance or not username:
            return render_template('ajouter_produit.html')
        try:
            date_echeance = datetime.strptime(date_echeance, '%Y-%m-%d')
            username = str(username)
            nouveau_produit = Product(name=nom_produit)
            db.session.add(nouveau_produit)
            db.session.commit()
            nouveau_detail = Product_detail(product_id=nouveau_produit.id, username=username, gamme=gamme, date_echeance=date_echeance, evolution_state=evolution_state)
            db.session.add(nouveau_detail)
            db.session.commit()
            for ingredient_id in ingredient_ids:
                ingredient = Ingredient.query.get(ingredient_id)
                if ingredient:
                    product_ingredient = Product_Ingredient(id_product=nouveau_produit.id, name_product=nouveau_produit.name, id_ingredient=ingredient.id, name_ingredient=ingredient.name)
                    db.session.add(product_ingredient)
            flash("Produit et détails ajoutés avec succès !", "success")
            return redirect(url_for('routes.dashboard'))
        except Exception as e:
            logger.debug(f"Erreur lors de l'ajout : {str(e)}", "error")
            flash(f"Erreur lors de l'ajout : {str(e)}", "error")
            return redirect(url_for('routes.dashboard'))
    ingredients = Ingredient.query.all()
    return render_template('ajouter_produit.html', ingredients=ingredients)

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
            db.session.commit()

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
                db.session.commit()

            db.session.commit()

            flash("Produit modifié avec succès !", "success")
            return redirect(url_for('routes.dashboard'))

        except Exception as e:
            logger.debug(f"Erreur lors de la modification : {str(e)}")
            flash(f"Erreur lors de la modification : {str(e)}", "error")
            return redirect(url_for('routes.modifier_produit', produit_id=produit_id))

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
        comments=comments
    )






def register_routes(app):
    app.register_blueprint(bp)