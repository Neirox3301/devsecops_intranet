from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, login_required, logout_user
from flask_wtf.csrf import generate_csrf
from werkzeug.security import check_password_hash
from models import User, Admin, Teacher, Student

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET'])
def login():
    return render_template('login.html', csrf_token=generate_csrf())


@auth_blueprint.route('/login', methods=['POST'])
def login_form():
    username = request.form['username']
    password = request.form['password']

    # Chercher l'utilisateur dans la base de données
    user = User.query.filter_by(username=username).first()
    pwhash = user.password if user else None
    if user and check_password_hash(pwhash, password):
        login_user(user)
        if user.role == 'student':
            session['student_id'] = Student.query.filter_by(user_id=user.id).first().id
            return redirect(url_for('dashboard.student_dashboard'))
        elif user.role == 'teacher':
            session['teacher_id'] = Teacher.query.filter_by(user_id=user.id).first().id
            return redirect(url_for('dashboard.teacher_dashboard'))
        elif user.role == 'admin':
            session['admin_id'] = Admin.query.filter_by(user_id=user.id).first().id
            return redirect(url_for('dashboard.admin_dashboard'))
        else:
            flash('Role inconnu', 'danger')
    else:
        flash(f'Username or password incorrect ', 'danger')
    return render_template('login.html')

@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
