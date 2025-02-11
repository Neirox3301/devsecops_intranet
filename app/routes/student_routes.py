import os
import secrets
from flask import Blueprint, render_template, redirect, url_for, send_file
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from flask_wtf.csrf import generate_csrf

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

from models import Grade, Class, Student, Subject, Assignment, TeacherClass, Teacher

student_dashboard_blueprint = Blueprint('student_dashboard', __name__)


# ----- Routes pour l'espace étudiant -----

@student_dashboard_blueprint.route('/student_dashboard/grades')
@login_required
def display_grades():
    """Affiche les notes de l'étudiant"""
    
    # Vérifier si l'utilisateur est conecté et est un étudiant
    if current_user.role != 'student':
        return redirect(url_for('auth.login', csrf_token=generate_csrf()))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    # if not student:
    #     return redirect(url_for('student_dashboard.no_grades'))

    student_grades = Grade.query.options(joinedload(Grade.subject)).filter_by(student_id=student.id).all()
    student_class = Class.query.filter_by(id=student.class_id).first()
    subjects = [{'id': grade.subject.id, 'name': grade.subject.name, 'grade': grade.grade} for grade in student_grades]

    temp_grades = Grade.query.all()
    temp_subjects = Subject.query.all()
    temp_assignments = Assignment.query.all()

    grades = [{'student_id': grade.student_id, 'subject_id': grade.subject_id, 'assignment_type_id': grade.assignment_type_id, 'grade': grade.grade} for grade in temp_grades if grade.student_id == student.id]
    assignments = [{'id': assignment.id, 'type': assignment.type} for assignment in temp_assignments]

    grade_dict = {
        subject.id: {
            assignment['type']: grade['grade']
            for grade in grades
            if grade['subject_id'] == subject.id
            for assignment in assignments
            if grade['assignment_type_id'] == assignment['id']
        }
        for subject in temp_subjects
    }
    # Ajout des notes manquantes
    for _, assignments_dict in grade_dict.items():
        for assignment in assignments:
            if assignment['type'] not in assignments_dict:
                assignments_dict[assignment['type']] = '--'
    

    return render_template('student_templates/student_grades.html', subjects=subjects, student_class=student_class, 
                           student=student, grades=grade_dict, assignments=assignments, csrf_token=generate_csrf())


@student_dashboard_blueprint.route('/student_dashboard/genereate_report_card')
@login_required
def generate_report_card():
    """Génère un bulletin de notes pour l'étudiant"""
    
    # Vérifier si l'utilisateur est conecté et est un étudiant
    if current_user.role != 'student':
        return redirect(url_for('auth.login', csrf_token=generate_csrf()))
    

    # Récupération des données de l'élève
    student = Student.query.filter_by(user_id=current_user.id).first()
    grades = Grade.query.filter_by(student_id=student.id).all()
    assignments = Assignment.query.all()
    subjects = Subject.query.all()
    
    # Création d'un dictionnaire pour les notes
    student_grades_dict = {subject.id: {assignment.id: '--' for assignment in assignments} for subject in subjects}
    for grade in grades:
        student_grades_dict[grade.subject_id][grade.assignment_type_id] = grade.grade

    # Calcul des moyennes
    student_averages = {}
    for subject in subjects:
        grade_number = len([grade.grade for grade in grades if grade.subject_id == subject.id and grade.grade != '--'])
        if grade_number == 0:
            student_averages[subject.id] = '--'
        else:
            student_averages[subject.id] = round(sum([grade.grade for grade in grades if grade.subject_id == subject.id]) / grade_number, 1)

    report_card = generate_report_card_function(student, subjects, assignments, student_grades_dict, student_averages)
    
    return report_card


@student_dashboard_blueprint.route('/student_dashboard/calendar')
@login_required
def display_calendar():
    """Affiche le calendrier de l'étudiant"""
    
    # Vérifier si l'utilisateur est conecté et est un étudiant
    if current_user.role != 'student':
        return redirect(url_for('auth.login', csrf_token=generate_csrf()))
    
    return render_template('student_templates/student_calendar.html', csrf_token=generate_csrf(), student = Student.query.filter_by(user_id=current_user.id).first())


@student_dashboard_blueprint.route('/student_dashboard/teachers')
@login_required
def display_teachers():
    """Affiche les enseignants de l'étudiant pour chaque matière"""
    
    # Vérifier si l'utilisateur est conecté et est un étudiant
    if current_user.role != 'student':
        return redirect(url_for('auth.login', csrf_token=generate_csrf()))
    
    class_ = Class.query.filter_by(id=current_user.student.class_id).first()
    subjects = Subject.query.all()
    teacherClasses = TeacherClass.query.filter_by(class_id=class_.id).all()
    teachers = Teacher.query.all()

    subject_dict = []
    for sub in subjects:
        teacher_found = False
        for tc in teacherClasses:
            if tc.subject_id == sub.id and tc.class_id == class_.id:
                for teacher in teachers:
                    if teacher.id == tc.teacher_id:
                        subject_dict.append({'name': sub.name, 'teacher': f"{teacher.first_name} {teacher.last_name}"})
                        teacher_found = True
                        break
            if teacher_found:
                break
        if not teacher_found:
            subject_dict.append({'name': sub.name, 'teacher': '--'})

    return render_template('student_templates/student_teachers.html', csrf_token=generate_csrf(), subjects=subject_dict)


@student_dashboard_blueprint.route('/student_dashboard/settings')
@login_required
def display_settings():
    """Affiche les paramètres de l'étudiant"""
    
    # Vérifier si l'utilisateur est conecté et est un étudiant
    if current_user.role != 'student':
        return redirect(url_for('auth.login', csrf_token=generate_csrf()))
    
    return render_template('student_templates/student_settings.html', student=Student.query.filter_by(user_id=current_user.id).first())


# Fonction pour gérer l'absence de notes
# @student_dashboard_blueprint.route('/student_dashboard/no_grades')
# @login_required
# def no_grades():
#     return render_template('student_templates/no_grades.html', message="Aucune note disponible pour le moment.")



# ----- Fonctions utilitaires -----

def generate_report_card_function(student: Student, subjects: list, assignments: list, student_grades_dict: dict, student_averages: dict):
    """Génère un bulletin de notes pour un étudiant"""
    
    # Création d'un buffer mémoire pour le PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []
    
    # Titre général du bulletin
    title = Paragraph(f"Bulletin de {student.last_name} {student.first_name}", styles["Title"])
    story.append(title)
    story.append(Spacer(1, 20))
    
    for sub in subjects:
        # Construction des données du tableau
        table_data = [
            [sub.name, "", ""],   # Ligne 0 : titre de la matière
            [assignment.type for assignment in assignments],  # Ligne 1 : en-tête des colonnes
            [student_grades_dict[sub.id][assignment.id] for assignment in assignments],  # Ligne 2 : notes
            [f"Moyenne élève : {student_averages[sub.id]}", "", ""]  # Ligne 3 : moyenne de l'élève
        ]
        
        col_width = doc.width / 3.0
        table = Table(table_data, colWidths=[col_width]*3)
        
        table_style = TableStyle([
            # Ligne 0 : Titre
            ('SPAN', (0,0), (2,0)),
            ('BACKGROUND', (0,0), (2,0), colors.lightblue),
            ('ALIGN', (0,0), (2,0), 'CENTER'),
            ('FONTSIZE', (0,0), (2,0), 12),
            ('BOTTOMPADDING', (0,0), (2,0), 8),
            
            # Ligne 1 : En-tête
            ('BACKGROUND', (0,1), (2,1), colors.lightgrey),
            ('ALIGN', (0,1), (2,1), 'CENTER'),
            ('FONTSIZE', (0,1), (2,1), 10),
            ('BOTTOMPADDING', (0,1), (2,1), 4),
            
            # Ligne 2 : Notes
            ('ALIGN', (0,2), (2,2), 'CENTER'),
            ('FONTSIZE', (0,2), (2,2), 10),
            ('BOTTOMPADDING', (0,2), (2,2), 8),
            
            # Ligne 3 : Moyenne de l'élève
            ('SPAN', (0,3), (2,3)),
            ('ALIGN', (0,3), (2,3), 'LEFT'),
            ('FONTSIZE', (0,3), (2,3), 10),
            ('BOTTOMPADDING', (0,3), (2,3), 8),
            
            # Bordure et grille
            ('BOX', (0,0), (2,-1), 1, colors.black),
            ('INNERGRID', (0,0), (2,-1), 0.5, colors.black),
        ])
        
        table.setStyle(table_style)
        story.append(table)
        story.append(Spacer(1, 30))
        
        # Calcul de la moyenne générale de l'élève
    valid_averages = [avg for avg in student_averages.values() if avg != '--']
    if valid_averages:
        overall_average = round(sum(valid_averages) / len(valid_averages), 1)
    else:
        overall_average = '--'

    # Détermination de l'appréciation en fonction de la moyenne générale
    if overall_average == '--':
        appreciation = "--"
    elif overall_average < 10:
        appreciation = "Avertissement de comportement et de travail"
    elif overall_average < 12:
        appreciation = "Avertissement de travail"
    elif overall_average < 14:
        appreciation = "Avertissement de comportement"
    elif overall_average < 16:
        appreciation = "Encouragements"
    else:
        appreciation = "Félicitations"

    # Création d'une table synthèse pour afficher la moyenne générale et l'appréciation
    synthese_data = [[f"Moyenne générale : {overall_average}", f"Appréciation : {appreciation}"]]
    synthese_table = Table(synthese_data, colWidths=[doc.width/2.0]*2)
    synthese_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(synthese_table)
    story.append(Spacer(1, 20))
    
    # Titre pour le commentaire du professeur principal
    comment_title = Paragraph("Commentaire du professeur principal :", styles["Heading3"])
    story.append(comment_title)
    story.append(Spacer(1, 5))
    
    # Commentaire du professeur principal
    negative_head_teacher_comments = [
        "Des efforts insuffisants, il faut travailler plus dur.",
        "Comportement perturbateur en classe.",
        "Participation insuffisante aux activités scolaires.",
        "Manque de motivation et de concentration.",
        "Doit améliorer son attitude en classe.",
        "Des résultats en dessous des attentes."
    ]
    
    positive_head_teacher_comments = [
        "Des progrès remarquables dans toutes les matières.",
        "Continuez à travailler dur et à rester concentré.",
        "Un élève modèle avec une attitude positive.",
        "Des efforts constants et une participation active.",
        "Très bon comportement en classe.",
        "Des compétences académiques solides et une grande curiosité.",
    ]

    if overall_average == '--' or overall_average < 10:
        head_teacher_comment = secrets.choice(negative_head_teacher_comments)
    else:
        head_teacher_comment = secrets.choice(positive_head_teacher_comments)

    # Création d'une grande case pour le commentaire du professeur principal
    comment_box_data = [[head_teacher_comment]]
    comment_box = Table(comment_box_data, colWidths=[doc.width], rowHeights=80)
    comment_box.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(comment_box)

    # --- Ajout d'un espace avant la section finale ---
    story.append(Spacer(1, 40))

    # Date et Lieu
    date_str = datetime.now().strftime("Fait à Lyon, le %d/%m/%Y")
    date_paragraph = Paragraph(date_str, styles["Normal"])
    story.append(date_paragraph)
    story.append(Spacer(1, 10))

    # Zone de signature 
    signature_data = [["Signature du Directeur / Professeur Principal"]]
    signature_table = Table(signature_data, colWidths=[doc.width])
    signature_table.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 1, colors.black),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('TOPPADDING', (0,0), (-1,0), 20),
    ]))
    story.append(signature_table)
    story.append(Spacer(1, 20))

    # Cachet officiel de l'école
    seal_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'seal.png')
    try:
        seal = Image(seal_path, width=80, height=80)
        seal.hAlign = 'RIGHT'
        story.append(seal)
    except Exception as e:
        pass

    # Mentions légales / Confidentialité
    legal_text = ("Ce document est confidentiel et destiné uniquement à l'élève concerné. "
                  "Toute diffusion ou reproduction sans autorisation est interdite.")
    legal_paragraph = Paragraph(legal_text, styles["Italic"])
    story.append(Spacer(1, 20))
    story.append(legal_paragraph)


    # Construction du document
    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="bulletin.pdf", mimetype='application/pdf')
    