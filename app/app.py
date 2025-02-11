import os
from dotenv import load_dotenv

from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from models.hash_passwords import hash_user_passwords
from cryptography.fernet import Fernet
from models.generate_key import generate_flask_secret_key

# Importation des blueprints
from routes.auth_routes import auth_blueprint
from routes.dashboard_routes import dashboard_blueprint
from routes.teacher_routes import teacher_dashboard_blueprint
from routes.student_routes import student_dashboard_blueprint
from routes.admin_routes import admin_dashboard_blueprint
from models import User, db


def load_secret_key():
    """Charge et déchiffre la clé secrète Flask avec Fernet. Si la clé n'existe pas, elle est générée."""
    try:
        print("[*] Chargement de la clé de chiffrement...")
        # Charger la clé de chiffrement
        with open(".venv/.flask_secret_key", "rb") as key_file:
            encryption_key = key_file.read()

        cipher = Fernet(encryption_key)
        print("[+] Clé de chiffrement chargée avec succès.")

        print("[*] Chargement et déchiffrement de la clé secrète Flask...")
        # Charger et déchiffrer la clé secrète Flask
        with open(".venv/flask_secret.enc", "rb") as secret_file:
            encrypted_secret = secret_file.read()

        decrypted_secret = cipher.decrypt(encrypted_secret)
        print("[+] Clé secrète Flask déchiffrée avec succès.")
        return decrypted_secret.decode()

    except Exception as e:
        print(f"[!] Erreur lors du chargement de la clé secrète : {e}")
        print("[*] Génération d'une nouvelle clé secrète...")

        # Générer une nouvelle clé secrète
        generate_flask_secret_key()

        try:
            print("[*] Réessayer de charger la clé de chiffrement...")
            # Réessayer de charger la clé de chiffrement
            with open(".venv/.flask_secret_key", "rb") as key_file:
                encryption_key = key_file.read()

            cipher = Fernet(encryption_key)
            print("[+] Clé de chiffrement chargée avec succès.")

            print("[*] Réessayer de charger et déchiffrer la clé secrète Flask...")
            # Réessayer de charger et déchiffrer la clé secrète Flask
            with open(".venv/flask_secret.enc", "rb") as secret_file:
                encrypted_secret = secret_file.read()

            decrypted_secret = cipher.decrypt(encrypted_secret)
            print("[+] Nouvelle clé secrète Flask déchiffrée avec succès.")
            return decrypted_secret.decode()

        except Exception as e:
            print(f"[!] Erreur lors de la génération et du chargement de la nouvelle clé secrète : {e}")
            return None


def create_app():
    """Crée une instance de l'application Flask."""
    app = Flask(__name__)

    # Configuration de l'application
    load_dotenv()
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    secret_key = load_secret_key()
    if secret_key:
        app.secret_key = secret_key
    else:
        raise ValueError("[!] Impossible d'utiliser la clé secrète Flask.")

    # Initialisation des extensions avec l'application
    db.init_app(app)  # Initialisation de SQLAlchemy
    login_manager.init_app(app)  # Initialisation de Flask-Login

    # Enregistrement des blueprints
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(dashboard_blueprint)
    app.register_blueprint(teacher_dashboard_blueprint)
    app.register_blueprint(student_dashboard_blueprint)
    app.register_blueprint(admin_dashboard_blueprint)
    
    # Protection CSRF
    csrf = CSRFProtect(app)

    # Sécurisation des en-têtes HTTP
    @app.after_request
    def set_security_headers(response):
        """Ajoute des en-têtes de sécurité pour protéger contre XSS, Clickjacking et autres attaques."""
        
        # Protection XSS avec Content Security Policy (CSP)
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' https://trusted-cdn.com; "
            "style-src 'self' https://trusted-cdn.com; "
            "img-src 'self' data:; "
            "frame-ancestors 'none';"  # Protection contre Clickjacking aussi
        )

        # Protection Clickjacking
        response.headers['X-Frame-Options'] = 'DENY'

        # Protection XSS avec X-XSS-Protection (utile pour vieux navigateurs)
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Protection contre sniffing MIME type
        response.headers['X-Content-Type-Options'] = 'nosniff'

        return response

    return app


login_manager = LoginManager()
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
