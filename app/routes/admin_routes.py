from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from models import User, Admin, Student, Teacher, Class, Subject, TeacherClass, TeacherSubject, db

admin_dashboard_blueprint = Blueprint('admin_dashboard', __name__)



# Helper function to check if a user has an associated account
def user_has_associated_account(user_id):
    student = Student.query.filter_by(user_id=user_id).first()
    teacher = Teacher.query.filter_by(user_id=user_id).first()
    admin = Admin.query.filter_by(user_id=user_id).first()
    return student or teacher or admin

# Helper function to delete a user if they don't have an associated account
def delete_user_if_no_associated_account(user):
    if not user_has_associated_account(user.id):
        db.session.delete(user)
        db.session.commit()


# Display the admin dashboard
@admin_dashboard_blueprint.route('/admin_dashboard/user_creation', methods=['GET', 'POST'])
@login_required
def user_creation_form(error_message=None):
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    # Get all the information needed to display the form
    role_objects = User.query.with_entities(User.role).distinct().all()
    roles = [{'name': role[0].strip()} for role in role_objects]
    
    return render_template('admin_templates/user_creation.html', roles=roles, error_message=error_message)


# Create a user
@admin_dashboard_blueprint.route('/admin_dashboard/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    # Clear the db session from a previous unfinished user creation
    last_user = User.query.order_by(User.id.desc()).first()
    delete_user_if_no_associated_account(last_user)
    
    # Get the information from the form
    chosen_username: str = request.form.get('username')
    chosen_password: str = request.form.get('password')
    chosen_confirmed_password: str = request.form.get('confirm_password')
    chosen_role: str = request.form.get('role')
    
    # Check if all the fields are filled
    if not all([chosen_username, chosen_password, chosen_confirmed_password, chosen_role]):
        return user_creation_form(error_message='Please fill all the fields')
    
    # Check in the User table to see if the username is already taken
    if User.query.filter_by(username=chosen_username).first():
        return user_creation_form(error_message='Username already taken')
     
    # Check if the password and the confirm password are the same
    if chosen_password != chosen_confirmed_password:
        return user_creation_form(error_message='Passwords do not match')

    # Clear the db session
    db.session.rollback()
    
    last_user = User.query.order_by(User.id.desc()).first()
    user_found: bool = False
    
    students = Student.query.all()
    teachers = Teacher.query.all()
    admins = Admin.query.all()
    
    while not user_found:
        for student in students:
            if student.user_id == last_user.id:
                user_found = True
                break
        for teacher in teachers:
            if teacher.user_id == last_user.id:
                user_found = True
                break
        for admin in admins:
            if admin.user_id == last_user.id:
                user_found = True
                break
        break
    
    if not user_found:
        return user_creation_form(error_message='You need to create a user first !')

    # Create the user
    try:
        pwhash = generate_password_hash(chosen_password, method='pbkdf2:sha256', salt_length=8)
        user = User(username=chosen_username, password=pwhash, role=chosen_role)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return user_creation_form(error_message=f'An error occurred : {e}')    
    
    # Redirect to the correct form
    if chosen_role == 'student':
        return redirect(url_for('admin_dashboard.student_creation_form'))
    elif chosen_role == 'teacher':
        return redirect(url_for('admin_dashboard.teacher_creation_form'))
    elif chosen_role == 'admin':
        return redirect(url_for('admin_dashboard.admin_creation_form'))
    else:
        delete_user_if_no_associated_account(user)
        return user_creation_form(error_message='Invalid role')



# Student creation form
@admin_dashboard_blueprint.route('/admin_dashboard/student_creation', methods=['GET', 'POST'])
@login_required
def student_creation_form(error_message=None, success_message=None):
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    # Get all the classes
    class_objects = Class.query.all()
    classes = [{'id': class_.id, 'name': class_.class_name} for class_ in class_objects]
    
    return render_template('admin_templates/student_creation.html', classes=classes, error_message=error_message)


# Student creation function
@admin_dashboard_blueprint.route('/admin_dashboard/create_student', methods=['GET', 'POST'])
@login_required
def create_student():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    # Redirect to the user creation form if the user is not committed yet, and just added to the session
    user = db.session.query(User).first()
    if not user:
        return user_creation_form(error_message='You need to create a user first!')
    
    chosen_first_name: str = request.form.get('first_name')
    chosen_last_name: str = request.form.get('last_name')
    chosen_class: int = int(request.form.get('class'))
    
    # Check if all the fields are filled
    if not all([chosen_first_name, chosen_last_name, chosen_class]):
        return student_creation_form(error_message='Please fill all the fields')
    
    try:
        user_id = db.session.query(User).order_by(User.id.desc()).first().id
        student = Student(first_name=chosen_first_name, last_name=chosen_last_name, user_id=user_id, class_id=chosen_class)
        db.session.add(student)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return student_creation_form(error_message=f'An error occurred : {e}')
    
    return student_creation_form(success_message=f'Student "{student.first_name}{student.last_name} created successfully')



# Teacher creation form
@admin_dashboard_blueprint.route('/admin_dashboard/teacher_creation', methods=['GET', 'POST'])
@login_required
def teacher_creation_form(error_message=None):
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    # Get all the classes
    class_objects = Class.query.all()
    classes = [{'id': class_.id, 'name': class_.class_name} for class_ in class_objects]
    
    subjects = Subject.query.all()
    subjects_dict = [{'id': subject.id, 'name': subject.name} for subject in subjects]
    
    return render_template('admin_templates/teacher_creation.html', classes=classes, subjects=subjects_dict, error_message=error_message)


# Teacher creation function
@admin_dashboard_blueprint.route('/admin_dashboard/create_teacher', methods=['GET', 'POST'])
@login_required
def create_teacher():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    first_name: str = request.form.get('first_name')
    last_name: str = request.form.get('last_name')
    subjects = request.form.getlist('subjects')
    
    class_subjects = {}
    for key in request.form:
        if '|' in key:  # Détecter les entrées des classes (ex: "class_id|subject_id")
            class_id, subject_id = key.split('|')
            if class_id not in class_subjects:
                class_subjects[class_id] = []
            class_subjects[class_id].append(subject_id)
    
    if not all([first_name, last_name, subjects, class_subjects]):
        return teacher_creation_form(error_message='Please fill all the fields')
    
    # Create the teacher and the associated subjects and classes
    try:
        last_user_id = db.session.query(User).order_by(User.id.desc()).first().id
        if not user_has_associated_account(last_user_id):
            teacher = Teacher(first_name=first_name, last_name=last_name, user_id=last_user_id)
            
            try:
                db.session.add(teacher)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return teacher_creation_form(error_message=f'An error occurred : {e}')
            
            teacher_subjects = [TeacherSubject(teacher_id=teacher.id, subject_id=subject_id) for subject_id in subjects]
            teacher_classes = []
            for class_id in class_subjects:
                for subject_id in class_subjects[class_id]:
                    teacher_classes.append(TeacherClass(teacher_id=teacher.id, class_id=class_id, subject_id=subject_id))

            db.session.add_all(teacher_subjects)
            db.session.add_all(teacher_classes)
            db.session.commit()
            
    except Exception as e:
        db.session.rollback()
        return teacher_creation_form(error_message=f'An error occurred : {e}')
    
    return teacher_creation_form()



# Admin creation form
@admin_dashboard_blueprint.route('/admin_dashboard/admin_creation', methods=['GET', 'POST'])
@login_required
def admin_creation(error_message=None):
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    classes = Class.query.all()
    classes_dict = [{'id': class_.id, 'name': class_.class_name} for class_ in classes]
    
    subjects = Subject.query.all()
    subjects_dict = [{'id': subject.id, 'name': subject.subject_name} for subject in subjects]
    
    return render_template('admin_templates/admin_creation.html', error_message=error_message, classes=classes_dict, subjects=subjects_dict)

# Admin creation function
@admin_dashboard_blueprint.route('/admin_dashboard/create_admin', methods=['GET', 'POST'])
@login_required
def create_admin():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    return redirect(url_for('admin_dashboard.admin_creation'))


@admin_dashboard_blueprint.route('/admin_dashboard/student_modification', methods=['GET', 'POST'])
@login_required
def student_modification(error_message=None, success_message=None, chosen_student=None):
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    students = Student.query.all()
    students_dict = [{'id': student.id, 'first_name': student.first_name, 'last_name': student.last_name, 'class_id': int(student.class_id)} for student in students]
    
    classes = Class.query.all()
    
    classes_dict = [{'id': class_.id, 'name': class_.class_name} for class_ in classes]
    classes = {class_.id: class_.class_name for class_ in classes}
    
    return render_template('admin_templates/student_modification.html', students=students_dict, classes=classes, 
                           classes_dict=classes_dict, chosen_student=chosen_student, 
                           error_message=error_message, success_message=success_message)


@admin_dashboard_blueprint.route('/admin_dashboard/modfify_student', methods=['GET', 'POST'])
@login_required
def modify_student():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))

    chosen_student = None
    if request.method == 'POST':
        chosen_student = request.form.get('student')
        if not chosen_student:
            return student_modification(error_message='Please choose a student')
        
        chosen_student = dict(Student.query.get(chosen_student).__dict__)
        print(f"Chosen student: {chosen_student}")
        return student_modification(chosen_student=chosen_student)


    student_id = request.form.get('student_id')
    chosen_first_name = request.form.get('first_name')
    chosen_last_name = request.form.get('last_name')
    chosen_class = request.form.get('class')
    
    if not all([student_id, chosen_first_name, chosen_last_name, chosen_class]):
        return student_modification(error_message='Please fill all the fields')
    
    try:
        student = Student.query.get(student_id)
        if student:
            student.first_name = chosen_first_name
            student.last_name = chosen_last_name
            student.class_id = chosen_class
            db.session.commit()
            return student_modification(success_message='Student modified successfully')
        else:
            return student_modification(error_message='Student not found')
    except Exception as e:
        db.session.rollback()
        return student_modification(error_message=f'An error occurred: {e}')



@admin_dashboard_blueprint.route('/admin_dashboard/teacher_subject_class_attribution', methods=['GET', 'POST'])
@login_required
def teacher_subject_class_attribution(error_message=None):
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    teachers = Teacher.query.all()
    teachers_dict = [{'id': teacher.id, 'first_name': teacher.first_name, 'last_name': teacher.last_name} for teacher in teachers]
    
    classes = Class.query.all()
    classes_dict = [{'id': class_.id, 'name': class_.class_name} for class_ in classes]
    
    subjects = Subject.query.all()
    subjects_dict = [{'id': subject.id, 'name': subject.name} for subject in subjects]
    
    return render_template('admin_templates/teacher_attribution.html', teachers=teachers_dict, classes=classes_dict, subjects=subjects_dict, error_message=error_message)


@admin_dashboard_blueprint.route('/admin_dashboard/attribute_teacher_to_subject_class', methods=['GET', 'POST'])
@login_required
def attribute_teacher_to_subject_class():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))

    pass