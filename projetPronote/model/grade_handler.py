from flask import Blueprint, request, redirect, url_for, session
from model.db_connection import get_db_connection

grade_handler_bp = Blueprint('grade_handler_bp', __name__)

@grade_handler_bp.route('/submit_grades', methods=['POST'])
def submit_grades():
    """Gère la soumission des notes et leur mise à jour dans la base de données"""
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('login_bp.home'))

    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('login_bp.home'))

    grades_data = request.form.to_dict(flat=False)  # Récupération des notes sous forme de dictionnaire

    if grades_data:
        for key, values in grades_data.items():
            # Clé sous forme "grades[student_id][subject]", valeur = liste des notes soumises
            if key.startswith("grades["):
                parts = key.strip("grades[").strip("]").split("][")
                if len(parts) == 2:
                    student_id, subject_id = parts
                    grade = values[0].strip()

                    if grade:  # Vérifie que la note n'est pas vide
                        conn.execute("""
                            INSERT INTO grades (grade, student_id, subject_id)
                            VALUES (?, ?, ?)
                            ON CONFLICT(student_id, subject_id) 
                            DO UPDATE SET grade=excluded.grade
                        """, (grade, student_id, subject_id))

        conn.commit()

    conn.close()
    return redirect(url_for('dashboard_prof_bp.grade_adder'))
