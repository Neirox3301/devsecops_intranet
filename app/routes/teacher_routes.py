from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from models import TeacherClass, Class, Student, Subject

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
    classes: dict = [{'id' : classes_id[i], 'name': classes_names[i]} for i in range(len(classes))]


    # Subjects
    subjects_id = tuple(set([tc.subject_id for tc in teacherClasses]))
    subjects_names = tuple(set([Subject.query.filter_by(id=id).first().name for id in subjects_id]))
    subjects : dict = [{'id' : subjects_id[i], 'name': subjects_names[i]} for i in range(len(subjects_id))]
    
    
    # Students
    students = []
    for class_id in classes_id:
        students_in_class = Student.query.filter_by(class_id=class_id).all()
        students.extend(students_in_class)
    
    return render_template('teacher_templates/teacher_grades.html', subjects=subjects, classes=classes_id, students=students)