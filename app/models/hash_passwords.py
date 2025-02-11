from werkzeug.security import generate_password_hash
from models import db, User


def hash_user_passwords():
    # Récupérer tous les utilisateurs
    users = User.query.all()

    for user in users:
        # Vérifier si le mot de passe est déjà haché
        if not user.password.startswith('pbkdf2:'):
            # Hacher le mot de passe
            hashed_password = generate_password_hash(user.password, method='pbkdf2:sha256', salt_length=8)
            user.password = hashed_password  # Mettre à jour le mot de passe haché
            db.session.commit()

    print("Tous les mots de passe ont été hachés.")
