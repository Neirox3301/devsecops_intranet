from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user

from models import TeacherClass, Class, Student, Subject, Grade, db

teacher_dashboard_blueprint = Blueprint('teacher_dashboard', __name__)


@teacher_dashboard_blueprint.route('/teacher_dashboard/grades', methods=['GET', 'POST'])
@login_required
def grades():
    teacherClasses = TeacherClass.query.filter_by(teacher_id=current_user.id).all()
    
    if not teacherClasses:
        # Put an error here
        return redirect(url_for('teacher_dashboard.'))
    
    # Classes
    classes_id: tuple[int] = tuple(set([tc.class_id for tc in teacherClasses]))
    classes_id = (1, 2, 3)
    classes = tuple(set([Class.query.filter_by(id=id).first() for id in classes_id]))
    classes_dict = sorted([{'id': class_.id, 'name': class_.class_name} for class_ in classes], key=lambda x: x['name'])

    # Subjects
    subjects_id = tuple(set([tc.subject_id for tc in teacherClasses]))
    subjects = tuple(set([Subject.query.filter_by(id=id).first() for id in subjects_id]))
    subjects_dict = sorted([{'id': subject.id, 'name': subject.name} for subject in subjects], key=lambda x: x['name'])
    
    # Initialize variables
    display_table = False
    students = []
    grades = []
    chosen_class = None
    chosen_subject = None

    
    if request.method == 'POST':
        requested_class = request.form.get('class')
        requested_subject = request.form.get('subject')
        
        # If the "filter" form is submitted
        if requested_class and requested_subject:
            for class_dict in classes_dict:
                if class_dict['id'] == int(requested_class):
                    chosen_class = class_dict
                    break
        
            for subject_dict in subjects_dict:
                if subject_dict['id'] == int(requested_subject):
                    chosen_subject = subject_dict
                    break
                
            display_table = True

            # Students
            students.extend(Student.query.filter_by(class_id=chosen_class['id']).all())

            # Grades
            grades_list = []
            for student in students:
                grades_list.extend(Grade.query.filter_by(student_id=student.id).all())
            for grade in grades_list:
                grades.append({'grade': grade.grade, 
                               'student_id': grade.student_id, 
                               'subject_id': grade.subject_id})

            # Add missing grades
            for student in students:
                grade_found = False
                for grade in grades:
                    if grade['student_id'] == student.id and grade['subject_id'] == chosen_subject['id']:
                        grade_found = True
                        break
                if not grade_found:
                    grades.append({'grade': '--', 'student_id': student.id, 'subject_id': chosen_subject['id']})

    return render_template('teacher_templates/teacher_grades.html', display_table=display_table, subjects=subjects_dict, classes=classes_dict, students=students, grades=grades, 
                           chosen_classe=chosen_class, chosen_subject=chosen_subject, grade_attributed=False)


@teacher_dashboard_blueprint.route('/teacher_dashboard/update_grades', methods=['GET', 'POST'])
@login_required
def update_grades():
    # Récupérer les grades envoyés par le formulaire
    grades = request.form

    to_add = []  
    to_update = [] 

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

    return grades()


