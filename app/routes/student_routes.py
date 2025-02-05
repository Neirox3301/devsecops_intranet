from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload

from models import Grade, Class, Student, Subject, Assignment

student_dashboard_blueprint = Blueprint('student_dashboard', __name__)

@student_dashboard_blueprint.route('/student_dashboard/grades')
@login_required
def display_grades():
    student = Student.query.filter_by(user_id=current_user.id).first()

    if not student:
        return redirect(url_for('student_dashboard.no_grades'))

    # Récupération des notes et des matières associées
    student_grades = Grade.query.options(joinedload(Grade.subject)).filter_by(student_id=student.id).all()

    if not student_grades:
        return redirect(url_for('student_dashboard.no_grades'))

    subjects = [{'id': grade.subject.id, 'name': grade.subject.name, 'grade': grade.grade} for grade in student_grades]

    student_class = Class.query.filter_by(id=student.class_id).first()


    temp_grades = Grade.query.all()
    temp_subjects = Subject.query.all()
    temp_assignments = Assignment.query.all()

    grades = [{'student_id': grade.student_id, 'subject_id': grade.subject_id, 'assignment_type_id': grade.assignment_type_id, 'grade': grade.grade} for grade in temp_grades if grade.student_id == student.id]
    assignments = [{'id': assignment.id, 'type': assignment.type} for assignment in temp_assignments]
    from typing import Dict, Any

    grade_dict: Dict[int, Dict[str, Any]] = {
        subject.id: {
            assignment['type']: grade['grade']
            for grade in grades
            if grade['subject_id'] == subject.id
            for assignment in assignments
            if grade['assignment_type_id'] == assignment['id']
        }
        for subject in temp_subjects
    }
    # Fill empty values with default grades
    for subject_id, assignments_dict in grade_dict.items():
        for assignment in assignments:
            if assignment['type'] not in assignments_dict:
                assignments_dict[assignment['type']] = '--'
    

    return render_template('student_templates/student_grades.html', subjects=subjects, student_class=student_class, student=student, grades=grade_dict, assignments=assignments)


@student_dashboard_blueprint.route('/student_dashboard/bulletins')
@login_required
def display_bulletins():
    return render_template('student_templates/student_bulletins.html')


@student_dashboard_blueprint.route('/student_dashboard/messagerie')
@login_required
def display_messagerie():
    return render_template('student_templates/student_messagerie.html')


@student_dashboard_blueprint.route('/student_dashboard/professeurs')
@login_required
def display_professeurs():
    return render_template('student_templates/student_professeurs.html')


@student_dashboard_blueprint.route('/student_dashboard/parametres')
@login_required
def display_parametres():
    return render_template('student_templates/student_parametres.html')


# Fonction pour gérer l'absence de notes
@student_dashboard_blueprint.route('/student_dashboard/no_grades')
@login_required
def no_grades():
    return render_template('student_templates/no_grades.html', message="Aucune note disponible pour le moment.")



