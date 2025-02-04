from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

student_dashboard_blueprint = Blueprint('student_dashboard', __name__)

# Exemple de la fonction pour afficher les notes, l'adresse sera localhost:5000/student_dashboard/grades
@student_dashboard_blueprint.route('/grades')
@login_required # A mettre devant toutes les fonctions ici, ca sert à vérifier à chaque requête que l'utilisateur est bien connecté
def display_grades():
    pass