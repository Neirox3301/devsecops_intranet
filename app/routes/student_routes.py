from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from models import Grade, Subject, Class

student_dashboard_blueprint = Blueprint('student_dashboard', __name__)

# Fonction pour afficher les notes de l'élève
@student_dashboard_blueprint.route('/student_dashboard/grades')
@login_required 
def display_grades():
    student_grades = Grade.query.filter_by(student_id=current_user.id).all()

    if not student_grades:
        return redirect(url_for('student_dashboard.'))

    # Récupérer les matières associées aux notes
    subjects = [{'id': grade.subject_id, 'name': Subject.query.filter_by(id=grade.subject_id).first().name, 'grade': grade.grade} for grade in student_grades]

    # Récupérer les informations sur la classe de l'élève
    student_class = Class.query.filter_by(id=current_user.class_id).first()

    return render_template('student_templates/student_grades.html', subjects=subjects, student_class=student_class)

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