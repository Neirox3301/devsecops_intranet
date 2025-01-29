from flask import Blueprint, render_template, request, redirect, url_for, session
from model.db_connection import get_db_connection  # Import correct

login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/')
def home():
    return render_template('index.html', message="")

@login_bp.route('/process', methods=['POST'])
def process():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return render_template('index.html', message="Veuillez remplir tous les champs.")

    conn = get_db_connection()
    if conn is None:
        return render_template('index.html', message="Erreur de connexion à la base de données.")

    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT CONCAT(LEFT(prenom, 1), nom) AS generated_username, status
        FROM users
        WHERE password = %s
        """
        cursor.execute(query, (password,))
        result = cursor.fetchone()

        if result:
            expected_username = result['generated_username']
            if username == expected_username:
                session['username'] = username
                return redirect(url_for('dashboard_bp.dashboard'))
            else:
                message = "Nom d'utilisateur incorrect."
        else:
            message = "Mot de passe incorrect ou utilisateur non trouvé."

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return render_template('index.html', message=message)
