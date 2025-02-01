from flask import Blueprint, render_template, request, redirect, url_for, session
from model.db_connection import get_db_connection

login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/')
def home():
    return render_template('index.html', message="")

@login_bp.route('/process', methods=['POST'])
def process():
    # Get the username and password from the form
    username = request.form.get('username')
    password = request.form.get('password')

    # Check if the username and password are not empty
    if not username or not password:
        return render_template('index.html', message="Veuillez remplir tous les champs.")

    conn = get_db_connection()
    if conn is None:
        return render_template('index.html', message="Erreur de connexion à la base de données.")

    # Get the user from the database
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT id, username, role
    FROM users
    WHERE username = %s AND password = %s;
    """
    cursor.execute(query, (username,password))
    result = cursor.fetchone()

    # If the user is found, store the username and role in the session
    if result:
        session['username'] = username
        session['role'] = result['role']
        session['id'] = result['id']
        
        if result['role'] == 'teacher':
            return redirect(url_for('dashboard_prof_bp.dashboard_prof'))
        else:
            return redirect(url_for('dashboard_bp.dashboard'))
        
    else:
        message = "Mot de passe incorrect ou utilisateur non trouvé."

    # Close the cursor and the connection
    if conn and conn.is_connected():
        cursor.close()
        conn.close()

    return render_template('index.html', message=message)
