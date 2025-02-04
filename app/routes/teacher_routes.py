from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user

from models import TeacherClass, Class, Student, Subject, Grade, db

teacher_dashboard_blueprint = Blueprint('teacher_dashboard', __name__)

@teacher_dashboard_blueprint.route('/teacher_dashboard/grades')
@login_required
def display_grades():
    teacherClasses = TeacherClass.query.filter_by(teacher_id=current_user.id).all()
    
    if not teacherClasses:
        # Put an error here
        return redirect(url_for('teacher_dashboard.'))
    
    # Classes
    classes_id: tuple[int] = tuple(set([tc.class_id for tc in teacherClasses]))
    classes_names: tuple[str] = tuple(set([Class.query.filter_by(id=id).first().class_name for id in classes_id]))
    classes: dict = [{'id' : classes_id[i], 'name': classes_names[i]} for i in range(len(classes_id))]
    classes_id = (1, 2, 3)

    # Subjects
    subjects_id = tuple(set([tc.subject_id for tc in teacherClasses]))
    subjects_names = tuple(set([Subject.query.filter_by(id=id).first().name for id in subjects_id]))
    subjects : dict = [{'id' : subjects_id[i], 'name': subjects_names[i]} for i in range(len(subjects_id))]
    
    
    # Students
    students: list[dict] = []
    for class_id in classes_id:
        students.extend(Student.query.filter_by(class_id=class_id).all())
        
        
    # Grades
    grades_list: list[dict] = []
    for student in students:
        grades_list.extend(Grade.query.filter_by(student_id=student.id).all())
    grades = []
    for grade in grades_list:
        grades.append({'grade': grade.grade, 
                       'student_id': grade.student_id, 
                       'subject_id': grade.subject_id})
    
    # Add missing grades
    for student in students:
        for subject in subjects:
            grade_found = False
            for grade in grades:
                if grade['student_id'] == student.id and grade['subject_id'] == subject['id']:
                    grade_found = True
                    break
            if not grade_found:
                grades.append({'grade': '--', 'student_id': student.id, 'subject_id': subject['id']})
    
    return render_template('teacher_templates/teacher_grades.html', subjects=subjects, students=students, grades=grades, grade_attributed=False)


@teacher_dashboard_blueprint.route('/teacher_dashboard/update_grades', methods=['GET', 'POST'])
@login_required
def update_grades():
    # Récupérer les grades envoyés par le formulaire
    grades = request.form
    print(grades)  # Pour déboguer et voir la structure des données

    to_add = []  # Liste pour les nouveaux grades à ajouter
    to_update = []  # Liste pour les grades existants à mettre à jour

    # Parcourir tous les inputs dans grades
    for grade_key, grade_value in grades.items():
        if grade_value == '':
            continue
        
        # grade_key aura la forme "student_id|subject_id"
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

    # Utiliser bulk_save_objects pour insérer de manière performante les nouvelles notes
    if to_add:
        db.session.bulk_save_objects(to_add)
    
    # Utiliser bulk_update_mappings pour mettre à jour les notes existantes
    if to_update:
        db.session.bulk_update_mappings(Grade, [{'grade': grade.grade, 'student_id': grade.student_id, 'subject_id': grade.subject_id} for grade in to_update])

    # Commit les modifications dans la base de données
    db.session.commit()

    return display_grades()
