from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, session
from app import db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('routes', __name__)

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
    return render_template('dashboard.html', user=user)

def register_routes(app):
    app.register_blueprint(bp)