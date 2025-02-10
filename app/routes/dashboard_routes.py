from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from flask_wtf.csrf import generate_csrf

dashboard_blueprint = Blueprint('dashboard', __name__)

@dashboard_blueprint.route('/student_dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))
    return render_template('student_templates/student_dashboard.html')

@dashboard_blueprint.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        return redirect(url_for('auth.login'))
    return render_template('teacher_templates/teacher_dashboard.html')

@dashboard_blueprint.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin_templates/admin_dashboard.html')