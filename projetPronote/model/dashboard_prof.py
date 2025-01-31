from flask import Blueprint, render_template, session, redirect, url_for
from model.db_connection import get_db_connection

dashboard_prof_bp = Blueprint('dashboard_prof_bp', __name__)

@dashboard_prof_bp.route('/dashboard_prof')
def dashboard_prof():
    if 'username' not in session:
        return redirect(url_for('login_bp.home'))

    username = session['username']
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('login_bp.home'))

    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT prenom, nom, status
        FROM users
        WHERE CONCAT(LEFT(prenom, 1), nom) = %s
        """
        cursor.execute(query, (username,))
        user_data = cursor.fetchone()
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    return render_template('dashboard_prof.html', user=user_data)
