from app import db

def reset_db():
    with app.app_context():
        db.session.execute('TRUNCATE TABLE ingredients') 
        db.session.execute('TRUNCATE TABLE product_states')
        db.session.execute('TRUNCATE TABLE projects')
        db.session.execute('TRUNCATE TABLE users')
        db.session.commit()
reset_db()
