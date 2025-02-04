from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

teacher_dashboard_blueprint = Blueprint('teacher_dashboard', __name__)

@teacher_dashboard_blueprint.route('/grades')
@login_required
def display_grades():
    pass