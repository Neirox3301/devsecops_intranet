from flask import Blueprint, render_template, session, redirect, url_for
from model.db_connection import get_db_connection

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login_bp.home'))

    user_id = session['id']

    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('login_bp.home'))

    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT id, first_name, last_name
    FROM students
    WHERE user_id = %s;
    """
    cursor.execute(query, (user_id,))
    user_data = cursor.fetchone()

    student_id = user_data['id']
    query2 = """
    SELECT grade
    FROM grades
    WHERE student_id = %s;
    """
    cursor.execute(query2, (student_id,))
    grade_data = cursor.fetchall()

    if conn.is_connected():
        cursor.close()
        conn.close()

    return render_template('dashboard.html', user=user_data, grades=grade_data)