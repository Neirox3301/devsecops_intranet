from flask import Blueprint, render_template, session, redirect, url_for
from model.db_connection import get_db_connection

dashboard_prof_bp = Blueprint('dashboard_prof_bp', __name__)

@dashboard_prof_bp.route('/dashboard_prof')
def dashboard_prof():
    if 'username' not in session:
        return redirect(url_for('login_bp.home'))

    username = session['username']
    id = session['id']
    
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('login_bp.home'))

    # Get the teacher's data
    cursor = conn.cursor(dictionary=True)
    user_info_query = """
    SELECT first_name, last_name
    FROM teachers
    WHERE user_id = %s;
    """
    cursor.execute(user_info_query, (id,))
    user_data = cursor.fetchone()
    
    # Get the teacher's subjects and classes
    get_all_id_query = """
    SELECT subject_id, class_id
    FROM teacher_classes
    WHERE teacher_id = %s;
    """
    cursor2 = conn.cursor(dictionary=True)
    cursor2.execute(get_all_id_query, (id,))
    all_id = cursor2.fetchall()
    subjects_id = [all_id[i]['subject_id'] for i in range(len(all_id))] # Convert dict to list of subject_ids
    classes_id = [all_id[i]['class_id'] for i in range(len(all_id))] # Convert dict to list of class_ids
    classes_id = (1, 2) # For testing purposes
    
    # Get the teacher's students
    placeholders = ', '.join(['%s'] * len(classes_id))
    get_students_query = f"""
    SELECT id, first_name, last_name
    FROM students
    WHERE class_id IN ({placeholders});
    """
    cursor3 = conn.cursor(dictionary=True)
    cursor3.execute(get_students_query, tuple(classes_id))
    students_data = cursor3.fetchall()  
    
    # Get the students' grades
    students_id = [students_data[i]['id'] for i in range(len(students_data))]
    
    if students_id and subjects_id:
        students_placeholders = ', '.join(['%s'] * len(students_id))
        subjects_placeholders = ', '.join(['%s'] * len(subjects_id))
        
        get_grades_query = f"""
        SELECT (SELECT name FROM subjects where ID = subject_id) AS subject_name, subject_id, student_id, grade
        FROM grades
        WHERE student_id IN ({students_placeholders}) 
        AND subject_id IN ({subjects_placeholders});
        """
        cursor4 = conn.cursor(dictionary=True)
        cursor4.execute(get_grades_query, students_id + subjects_id)
        grades_data = cursor4.fetchall()
    
    # Only keep the grades of the students of the teacher
    grades_data = [grades_data[i] for i in range(len(grades_data)) if grades_data[i]['student_id'] in students_id]
    
    # Only keep one of each subjects (to avoid duplicates in the table)
    subjects_data = tuple(set([grades_data[i]['subject_name'] for i in range(len(grades_data))]))
    
    # Close the cursor and the connection
    if conn.is_connected():
        cursor.close()
        conn.close()

    return render_template('dashboard_prof.html', user=user_data, classes=classes_id, students=students_data, grades=grades_data, subjects=subjects_data)
