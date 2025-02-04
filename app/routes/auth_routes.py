from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from models import User

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Chercher l'utilisateur dans la base de données
        user = User.query.filter_by(username=username).first()
        pwhash = user.password
        if user and check_password_hash(pwhash, password):
            login_user(user)
            if user.role == 'student':
                return redirect(url_for('dashboard.student_dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('dashboard.teacher_dashboard'))
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
