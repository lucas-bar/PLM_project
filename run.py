from app import db, app
from flask_migrate import Migrate


# Créer la base de données
with app.app_context():
    db.create_all()

# Lancer l'application
if __name__ == '__main__':
    app.run(debug=True)