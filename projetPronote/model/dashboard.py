from flask import Blueprint, render_template, session, redirect, url_for
from model.db_connection import get_db_connection

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login_bp.home'))

    username = session['username']
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('login_bp.home'))

    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT prenom, nom, notes_matiere1, notes_matiere2, notes_matiere3, notes_matiere4, notes_matiere5
        FROM users
        WHERE CONCAT(LEFT(prenom, 1), nom) = %s
        """
        cursor.execute(query, (username,))
        user_data = cursor.fetchone()
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    return render_template('dashboard.html', user=user_data)
