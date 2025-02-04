from flask import Flask, redirect, url_for
from flask_login import LoginManager
from models.hashing_machine import hash_user_passwords
from models import db

# Création de l'instance de LoginManager
login_manager = LoginManager()

# Importation des blueprints
from routes.auth_routes import auth_blueprint
from routes.dashboard_routes import dashboard_blueprint
from routes.teacher_routes import teacher_dashboard_blueprint
from routes.student_routes import student_dashboard_blueprint
from models import User  # Importation du modèle User

def create_app():
    app = Flask(__name__)

    # Configuration de l'application
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/academis' # Changer root:mdp par son propre mdp
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'mon_secret_key'

    # Initialisation des extensions avec l'application
    db.init_app(app)  # Initialisation de SQLAlchemy
    login_manager.init_app(app)  # Initialisation de Flask-Login

    # Enregistrement des blueprints
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(dashboard_blueprint)
    app.register_blueprint(teacher_dashboard_blueprint)
    app.register_blueprint(student_dashboard_blueprint)

    return app

app = create_app()

# Hashage des mots de passe
with app.app_context():
    hash_user_passwords()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Charge l'utilisateur depuis la base de données

@app.route('/')
def home():
    return redirect(url_for('auth.login'))  # Redirige vers la page de login

if __name__ == '__main__':
    app.run(debug=True)
