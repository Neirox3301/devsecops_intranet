from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuration de l'application Flask
app.config['SECRET_KEY'] = 'secret!'  # Change la clé secrète par une valeur sécurisée
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/academis'  # Remplace avec ta config MySQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_REGISTERABLE'] = True  # Permet l'inscription des utilisateurs
app.config['SECURITY_PASSWORD_SALT'] = 'some_salt'  # Ajoute un sel pour le hachage des mots de passe

# Initialisation de la base de données
db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('teacher', 'student', name='role_enum'), nullable=False)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)

# Initialisation de Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, None)
security = Security(app, user_datastore)

from model.login_check import login_bp
from model.dashboard import dashboard_bp
from model.dashboard_prof import dashboard_prof_bp

app.register_blueprint(login_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(dashboard_prof_bp)

if __name__ == '__main__':
    app.run(debug=True)
