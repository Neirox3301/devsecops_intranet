from flask import Blueprint, render_template, session, redirect, url_for
from model.db_connection import get_db_connection

dashboard_prof_bp = Blueprint('dashboard_prof_bp', __name__)

@dashboard_prof_bp.route('/dashboard_prof')
def dashboard_prof():
    if 'username' not in session:
        return redirect(url_for('login_bp.home'))

    user_id = session['id']
    
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('login_bp.home'))

    # Get the teacher's data
    user_info_query = """
    SELECT first_name, last_name
    FROM teachers
    WHERE user_id = %s;
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(user_info_query, (user_id,))
    user_data = cursor.fetchone()
    
    # Get the teacher's subjects and classes
    get_all_id_query = """
    SELECT subject_id, class_id
    FROM teacher_classes
    WHERE teacher_id = %s;
    """
    cursor.execute(get_all_id_query, (user_id,))
    all_id = cursor.fetchall()
    subjects_id = [item['subject_id'] for item in all_id]
    classes_id = [item['class_id'] for item in all_id]
    
    # For testing purposes
    classes_id = (1, 2)
    
    # Get the teacher's students
    placeholders = ', '.join(['%s'] * len(classes_id))
    get_students_query = f"""
    SELECT id, first_name, last_name
    FROM students
    WHERE class_id IN ({placeholders});
    """
    cursor.execute(get_students_query, tuple(classes_id))
    students_data = cursor.fetchall()
    
    # Get the students' grades
    students_id = [student['id'] for student in students_data]
    
    grades_data = []
    if students_id and subjects_id:
        students_placeholders = ', '.join(['%s'] * len(students_id))
        subjects_placeholders = ', '.join(['%s'] * len(subjects_id))
        
        get_grades_query = f"""
        SELECT (SELECT name FROM subjects WHERE ID = subject_id) AS subject_name, subject_id, student_id, grade
        FROM grades
        WHERE student_id IN ({students_placeholders}) 
        AND subject_id IN ({subjects_placeholders});
        """
        cursor.execute(get_grades_query, students_id + subjects_id)
        grades_data = cursor.fetchall()
    
    # Only keep the grades of the students of the teacher
    grades_data = [grade for grade in grades_data if grade['student_id'] in students_id]

    # Get the subjects names
    subjects_placeholders = ', '.join(['%s'] * len(subjects_id))
    get_students_query = f"""
    SELECT id, name
    FROM subjects
    WHERE id IN ({subjects_placeholders});
    """
    cursor.execute(get_students_query, tuple(subjects_id))
    subjects = cursor.fetchall()


    # Add rows for students without grades and set their grade to "--"
    for student in students_data:
        for subject in subjects:
            if not any(grade['student_id'] == student['id'] and grade['subject_id'] == subject['id'] for grade in grades_data):
                grades_data.append({
                    'subject_name': next(subject['name'] for grade in grades_data if grade['subject_id'] == subject['id']),
                    'subject_id': subject['id'],
                    'student_id': student['id'],
                    'grade': '--'
                })
    
    # Only keep one of each subjects (to avoid duplicates in the table)
    subjects_data = tuple(set(grade['subject_name'] for grade in grades_data))
    
    # Close the cursor and the connection
    cursor.close()
    conn.close()

    return render_template('dashboard_prof.html', user=user_data, classes=classes_id, students=students_data, grades=grades_data, subjects=subjects_data)
