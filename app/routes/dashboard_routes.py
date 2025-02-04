from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

dashboard_blueprint = Blueprint('dashboard', __name__)

@dashboard_blueprint.route('/student_dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))
    # Ajouter des informations spécifiques à l'élève
    return render_template('student_templates/student_dashboard.html')

@dashboard_blueprint.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        return redirect(url_for('auth.login'))
    # Ajouter des informations spécifiques au professeur
    return render_template('teacher_templates/teacher_dashboard.html')
