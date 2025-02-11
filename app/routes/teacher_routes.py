from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from flask_wtf.csrf import generate_csrf

from models import Teacher, TeacherClass, Class, Student, Subject, Grade, Assignment, db

teacher_dashboard_blueprint = Blueprint('teacher_dashboard', __name__)


# ----- Routes pour l'espace enseignant ----- 

@teacher_dashboard_blueprint.route('/teacher_dashboard/grades', methods=['GET'])
@login_required
def grades():
    """Affiche les notes des élèves"""
    
    # Vérifier si l'utilisateur est connecté et est un enseignant
    if current_user.role != 'teacher':
        return redirect(url_for('home', csrf_token=generate_csrf()))
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    teacherClasses = TeacherClass.query.filter_by(teacher_id=current_user.id).all()

    if not teacherClasses:
        # Put an error here
        return redirect(url_for('teacher_dashboard.'))
    
    # Classes
    classes_id: tuple[int] = tuple(set([tc.class_id for tc in teacherClasses]))
    classes_id = (1, 2, 3)
    classes = tuple(set([Class.query.filter_by(id=id).first() for id in classes_id]))
    classes_dict = sorted([{'id': class_.id, 'name': class_.class_name} for class_ in classes], key=lambda x: x['name'])

    # Matières
    subjects_id = tuple(set([tc.subject_id for tc in teacherClasses]))
    subjects = tuple(set([Subject.query.filter_by(id=id).first() for id in subjects_id]))
    subjects_dict = sorted([{'id': subject.id, 'name': subject.name} for subject in subjects], key=lambda x: x['name'])
    
    # Types de devoirs
    assignments = Assignment.query.all()
    assignments_dict = sorted([{'id': assignment.id, 'type': assignment.type} for assignment in assignments], key=lambda x: x['id'])
    
    # Initialiser les variables
    display_table = False
    students = []
    grades = []
    chosen_class = None
    chosen_subject = None
    chosen_assignment = None

    return render_template('teacher_templates/teacher_grades.html', teacher=teacher, display_table=display_table, subjects=subjects_dict, 
                           classes=classes_dict, assignments=assignments_dict, students=students, grades=grades, 
                           chosen_classe=chosen_class, chosen_subject=chosen_subject, chosen_assignment=chosen_assignment, 
                           grade_attributed=False, csrf_token=generate_csrf())
    
    
@teacher_dashboard_blueprint.route('/teacher_dashboard/grades', methods=['POST'])
@login_required
def grades_form():
    """Affiche les notes des élèves en fonction des filtres"""
    
    # Vérifier si l'utilisateur est connecté et est un enseignant
    if current_user.role != 'teacher':
        return redirect(url_for('home', csrf_token=generate_csrf()))
    
    # Récupérer la table de liaison entre les classes et les matières
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    teacherClasses = TeacherClass.query.filter_by(teacher_id=current_user.id).all()

    if not teacherClasses:
        # Put an error here TODO
        return redirect(url_for('teacher_dashboard.'))
    
    # Récupérer les classes
    classes_id: tuple[int] = tuple(set([tc.class_id for tc in teacherClasses]))
    classes_id = (1, 2, 3)
    classes = tuple(set([Class.query.filter_by(id=id).first() for id in classes_id]))
    classes_dict = sorted([{'id': class_.id, 'name': class_.class_name} for class_ in classes], key=lambda x: x['name'])

    # Récupérer les matières
    subjects_id = tuple(set([tc.subject_id for tc in teacherClasses]))
    subjects = tuple(set([Subject.query.filter_by(id=id).first() for id in subjects_id]))
    subjects_dict = sorted([{'id': subject.id, 'name': subject.name} for subject in subjects], key=lambda x: x['name'])
    
    # Récupérer les types de devoirs
    assignments = Assignment.query.all()
    assignments_dict = sorted([{'id': assignment.id, 'type': assignment.type} for assignment in assignments], key=lambda x: x['id'])
    
    # Initialiser les variables
    display_table = False
    students = []
    grades = []
    chosen_class = None
    chosen_subject = None
    chosen_assignment = None

    # Récupérer les valeurs du formulaire
    requested_class = request.form.get('class')
    requested_subject = request.form.get('subject')
    requested_assignment = request.form.get('assignment')
    
    # Si le formulaire "filtres" a été soumis
    if requested_class and requested_subject and requested_assignment:
        for class_dict in classes_dict:
            if class_dict['id'] == int(requested_class):
                chosen_class = class_dict
                break
    
        for subject_dict in subjects_dict:
            if subject_dict['id'] == int(requested_subject):
                chosen_subject = subject_dict
                break
            
        for assignment_dict in assignments_dict:
            if assignment_dict['id'] == int(requested_assignment):
                chosen_assignment = assignment_dict
                break
            
        display_table = True

        # Récupérer les étudiants
        students.extend(Student.query.filter_by(class_id=chosen_class['id']).all())

        # Récupérer les notes
        grades_list = []
        for student in students:
            grades_list.extend(Grade.query.filter_by(student_id=student.id).all())
        for grade in grades_list:
            grades.append({'grade': grade.grade, 
                            'student_id': grade.student_id, 
                            'subject_id': grade.subject_id,
                            'assignment_type_id': grade.assignment_type_id
                            })

        # Rajouter les notes manquantes
        for student in students:
            grade_found = False
            for grade in grades:
                if grade['student_id'] == student.id and grade['subject_id'] == chosen_subject['id'] and grade['assignment_type_id'] == chosen_assignment['id']:
                    grade_found = True
                    break
            if not grade_found:
                grades.append({'grade': '--', 'student_id': student.id, 'subject_id': chosen_subject['id'], 'assignment_type_id': chosen_assignment['id']})
                
        # Trier les notes selon les types de devoirs
        grades = [grade for grade in grades if grade['assignment_type_id'] == chosen_assignment['id']]

    return render_template('teacher_templates/teacher_grades.html', teacher=teacher, display_table=display_table, subjects=subjects_dict, 
                           classes=classes_dict, assignments=assignments_dict, students=students, grades=grades, 
                           chosen_classe=chosen_class, chosen_subject=chosen_subject, chosen_assignment=chosen_assignment, 
                           grade_attributed=False, csrf_token=generate_csrf())


@teacher_dashboard_blueprint.route('/teacher_dashboard/update_grades', methods=['POST'])
@login_required
def update_grades():
    """Mets à jour les notes des élèves"""
    
    # Vérifier si l'utilisateur est connecté et est un enseignant
    if current_user.role != 'teacher':
        return redirect(url_for('home', csrf_token=generate_csrf()))
    
    # Récupérer les notes envoyés par le formulaire
    grades = request.form

    to_add = []  
    to_update = [] 

    # Parcourir tous les inputs dans grades
    for grade_key, grade_value in grades.items():
        if grade_value == '':
            continue
        
        # grade_key a la forme "student_id|subject_id"
        student_id, subject_id = map(int, grade_key.split('|'))  # Séparer et convertir en int
        
        # Vérifier si une note existe déjà pour cet étudiant et cette matière
        existing_grade = Grade.query.filter_by(student_id=student_id, subject_id=subject_id).first()

        if existing_grade:
            # Si la note existe, la mettre à jour
            existing_grade.grade = grade_value
            to_update.append(existing_grade)
        else:
            # Si la note n'existe pas, créer une nouvelle entrée
            new_grade = Grade(student_id=student_id, subject_id=subject_id, grade=grade_value)
            to_add.append(new_grade)

    if to_add:
        db.session.bulk_save_objects(to_add)
    
    if to_update:
        db.session.bulk_update_mappings(Grade, [{'grade': grade.grade, 'student_id': grade.student_id, 'subject_id': grade.subject_id} for grade in to_update])

    db.session.commit()
    
    return grades()

@teacher_dashboard_blueprint.route('/teacher_dashboard/bulletins')
@login_required
def display_bulletins():
    """""" # TODO
    
    # Vérifier si l'utilisateur est connecté et est un enseignant
    if current_user.role != 'teacher':
        return redirect(url_for('home', csrf_token=generate_csrf()))
    
    return render_template('teacher_templates/teacher_bulletins.html', csrf_token=generate_csrf())


@teacher_dashboard_blueprint.route('/teacher_dashboard/calendar')
@login_required
def display_calendar():
    """Affiche le calendrier de l'enseignant"""
    
    # Vérifier si l'utilisateur est connecté et est un enseignant
    if current_user.role != 'teacher':
        return redirect(url_for('home', csrf_token=generate_csrf()))
    
    return render_template('teacher_templates/teacher_calendar.html',csrf_token=generate_csrf(), teacher = Teacher.query.filter_by(user_id=current_user.id).first())


@teacher_dashboard_blueprint.route('/teacher_dashboard/students')
@login_required
def display_students():
    """Affiche les élèves de l'enseignant et leur classe"""
    
    # Vérifier si l'utilisateur est connecté et est un enseignant
    if current_user.role != 'teacher':
        return redirect(url_for('home', csrf_token=generate_csrf()))
    
    # Récupérer les classes de l'enseignant
    teacherclasses = TeacherClass.query.filter_by(teacher_id=current_user.id).all()
    classes = [Class.query.filter_by(id=tc.class_id).first() for tc in teacherclasses]
    
    # Récupérer les élèves de chaque classe
    students = []
    for class_ in classes:
        students.extend(Student.query.filter_by(class_id=class_.id).all())
        
    student_dict = [{'id': student.id, 'name': f'{student.last_name} {student.first_name}', 'class_name': Class.query.filter_by(id=student.class_id).first().class_name} for student in students]
    
    return render_template('teacher_templates/teacher_students.html', students=student_dict)


@teacher_dashboard_blueprint.route('/teacher_dashboard/settings')
@login_required
def display_settings():
    """Affiche les paramètres de l'enseignant"""
    
    # Vérifier si l'utilisateur est connecté et est un enseignant
    if current_user.role != 'teacher':
        return redirect(url_for('home', csrf_token=generate_csrf()))
    
    return render_template('teacher_templates/teacher_settings.html',  teacher=Teacher.query.filter_by(user_id=current_user.id).first())