from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user

from models import User, Admin, Student, Teacher, Class

admin_dashboard_blueprint = Blueprint('admin_dashboard', __name__)

@admin_dashboard_blueprint.route('/admin_dashboard/user_creation', methods=['POST'])
@login_required
def display_user_creation_form():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    
    # Get all the information needed to display the form
    users = User.query.all()
    classes = Class.query.all()
    
    # Get all the roles from the User class
    roles = User.__table__.columns['role'].type.enums
    
    
    # TODO : check in the User table to see if the username is already taken
    
    
    return render_template('admin_templates/admin_user_creation.html', roles=[])


@admin_dashboard_blueprint.route('/admin_dashboard/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    chosen_first_name: str = request.form.get('first_name')
    chosen_last_name: str = request.form.get('last_name')
    chosen_username: str = request.form.get('username')
    chosen_password: str = request.form.get('password')
    chosen_confirmed_password: str = request.form.get('confirm_password')
    chosen_role: str = request.form.get('role')
    
    if not all([chosen_first_name, chosen_last_name, chosen_username, chosen_password, chosen_confirmed_password, chosen_role]):
        return redirect(url_for('admin_dashboard.display_user_creation_form')) # How do you flash a message to warn the user of the problem
    
    # Check if the password and the confirm password are the same
    if chosen_password != chosen_confirmed_password:
        return redirect(url_for('admin_dashboard.display_user_creation_form'))
    
    
    
    
    
    
    
    return redirect(url_for('admin_dashboard.display_user_creation_form'))


@admin_dashboard_blueprint.route('/admin_dashboard/create_student', methods=['GET', 'POST'])
@login_required
def create_student():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    return redirect(url_for('admin_dashboard.display_user_creation_form'))


@admin_dashboard_blueprint.route('/admin_dashboard/create_teacher', methods=['GET', 'POST'])
@login_required
def create_teacher():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    return redirect(url_for('admin_dashboard.display_user_creation_form'))