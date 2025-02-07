from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from models import User, Admin, Student, Teacher, Class, Subject, TeacherClass, TeacherSubject, Grade, db

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
        
        
def delete_student(student_id):
    student = Student.query.get(student_id)
    if student:
        try:
            user = User.query.get(student.user_id)
            grades = Grade.query.filter_by(student_id=student.id).all()
            
            for grade in grades:
                db.session.delete(grade)
            db.session.delete(student)
            db.session.delete(user)

            db.session.commit()
            return True
        
        except:
            db.session.rollback()
            return False
        
    return False


def delete_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if teacher:
        try:
            user = User.query.get(teacher.user_id)
            teacher_classes = TeacherClass.query.filter_by(teacher_id=teacher.id).all()
            teacher_subjects = TeacherSubject.query.filter_by(teacher_id=teacher.id).all()
            
            # TODO : Set the head teacher to None if the teacher is the head teacher of a class
            
            
            for teacher_class in teacher_classes:
                db.session.delete(teacher_class)
            for teacher_subject in teacher_subjects:
                db.session.delete(teacher_subject)
            db.session.delete(teacher)
            db.session.delete(user)
            
            db.session.commit()
            return True
        
        except:
            db.session.rollback()
            return False
        
    return False



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
def student_modification():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    # Get all the students and classes from the database
    students = Student.query.all()
    students_dict = [{'id': student.id, 'first_name': student.first_name, 'last_name': student.last_name, 'class_id': int(student.class_id)} for student in students]
    
    classes = Class.query.all()
    classes_dict = [{'id': class_.id, 'name': class_.class_name} for class_ in classes]
    classes = {class_.id: class_.class_name for class_ in classes}
    
    # Initialize the variables
    chosen_student = None
    student_id = None
    chosen_first_name = None
    chosen_last_name = None
    chosen_class = None
    error_message = None
    success_message = None
    
    # Once a student is chosen, display the form with the student's information
    if request.method == 'POST':
        chosen_student_id = request.form.get('chosen_student_id')
        if chosen_student_id:
            chosen_student = [student for student in students_dict if student['id'] == int(chosen_student_id)][0] if chosen_student_id else None
            
        information_form_submitted = request.form.get('information_form_submitted')
        if not information_form_submitted:
            return render_template('admin_templates/student_modification.html', students=students_dict, classes=classes, 
                                   classes_dict=classes_dict, chosen_student=chosen_student, 
                                   error_message=error_message, success_message=success_message)
        
        
        # Get the user from the form
        student_id = int(request.form.get('chosen_student_id'))
        student = Student.query.get(student_id)
        
        if not student:
            error_message = 'Student not found'
            return render_template('admin_templates/student_modification.html', students=students_dict, classes=classes, 
                                   classes_dict=classes_dict, chosen_student=chosen_student, 
                                   error_message=error_message, success_message=success_message)
        
        
        action = request.form.get('action')
        if action == 'delete':
            try:
                student_deleted = delete_student(student_id)
                if student_deleted:
                    success_message='Student deleted successfully'
                    return redirect(url_for('admin_dashboard.student_modification'))
                
                else:
                    error_message='An error occurred while deleting the student'
                    return render_template('admin_templates/student_modification.html', students=students_dict, classes=classes, 
                                   classes_dict=classes_dict, chosen_student=chosen_student, 
                                   error_message=error_message, success_message=success_message)
            except Exception as e:
                db.session.rollback()
                error_message=f'An error occurred: {e}'
            
        elif action == 'modify':
            # Get the information from the form
            chosen_first_name = request.form.get('first_name')
            chosen_last_name = request.form.get('last_name')
            chosen_class = int(request.form.get('selected_class'))
            
            # Check if all the fields are filled
            if not all([chosen_first_name, chosen_last_name, chosen_class]):
                render_template('admin_templates/student_modification.html', students=students_dict, classes=classes, 
                           classes_dict=classes_dict, chosen_student=chosen_student, 
                           error_message=error_message, success_message=success_message)
        
            # Modify the student in the database
            try:
                student.first_name = chosen_first_name
                student.last_name = chosen_last_name
                student.class_id = chosen_class
                db.session.commit()
                return redirect(url_for('admin_dashboard.student_modification'))
                
            except Exception as e:
                db.session.rollback()
                error_message=f'An error occurred: {e}'
    
    return render_template('admin_templates/student_modification.html', students=students_dict, classes=classes, 
                           classes_dict=classes_dict, chosen_student=chosen_student, 
                           error_message=error_message, success_message=success_message)



@admin_dashboard_blueprint.route('/admin_dashboard/teacher_modification', methods=['GET', 'POST'])
@login_required
def teacher_modification():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    # Get all the teachers and classes from the database
    teacher_classes = TeacherClass.query.all()
    teacher_classes_dict = [{'teacher_id': teacher_class.teacher_id, 'class_id': teacher_class.class_id, 'subject_id': teacher_class.subject_id} for teacher_class in teacher_classes]
    
    classes = Class.query.all()
    classes_dict = [{'id': class_.id, 'name': class_.class_name, 'head_teacher_id': class_.head_teacher_id} for class_ in classes]
    classes = {class_.id: class_.class_name for class_ in classes}
    
    teachers = Teacher.query.all()
    teachers_dict = [{'id': teacher.id, 'first_name': teacher.first_name, 
                      'last_name': teacher.last_name, 
                      'head_teacher_classes': [class_['class_id'] for class_ in classes_dict if class_['head_teacher_id']] == teacher.id,
                      'classes': [class_['class_id'] for class_ in teacher_classes_dict if class_['teacher_id'] == teacher.id]} for teacher in teachers]
    

    
    # Initialize the variables
    chosen_teacher = None
    teacher_id = None
    chosen_first_name = None
    chosen_last_name = None
    chosen_class = None
    error_message = None
    success_message = None
    teacher_classes = None
    
    # Once a teacher is chosen, display the form with the teacher's information
    if request.method == 'POST':        
        chosen_teacher_id = request.form.get('chosen_teacher_id')
        if chosen_teacher_id:
            chosen_teacher = [teacher for teacher in teachers_dict if teacher['id'] == int(chosen_teacher_id)][0] if chosen_teacher_id else None
            
        information_form_submitted = request.form.get('information_form_submitted')
        if not information_form_submitted:
            return render_template('admin_templates/teacher_modification.html', teachers=teachers_dict, classes=classes, 
                                   classes_dict=classes_dict, chosen_teacher=chosen_teacher, 
                                   error_message=error_message, success_message=success_message)
        
        # Get the user from the form
        teacher = Teacher.query.get(chosen_teacher_id)
        if not teacher:
            error_message = 'teacher not found'
            return render_template('admin_templates/teacher_modification.html', teachers=teachers_dict, classes=classes, 
                                   classes_dict=classes_dict, chosen_teacher=chosen_teacher, 
                                   error_message=error_message, success_message=success_message)
        
        action = request.form.get('action')
        if action == 'delete':
            try:
                teacher_deleted = delete_teacher(teacher_id)
                if teacher_deleted:
                    success_message='Teacher deleted successfully'
                    return redirect(url_for('admin_dashboard.teacher_modification'))
                
                else:
                    error_message='An error occurred while deleting the teacher'
                    return render_template('admin_templates/teacher_modification.html', teachers=teachers_dict, classes=classes, 
                                   classes_dict=classes_dict, chosen_teacher=chosen_teacher, 
                                   error_message=error_message, success_message=success_message)
            except Exception as e:
                db.session.rollback()
                error_message=f'An error occurred: {e}'
            
        elif action == 'modify':
            # Get the information from the form
            chosen_first_name = request.form.get('first_name')
            chosen_last_name = request.form.get('last_name')
            chosen_classes = request.form.getlist('selected_classes')
            chosen_classes = list(map(int, chosen_classes)) if chosen_classes else []
            print(f'Chosen classes: {chosen_classes}')
            
            # Check if all the fields are filled
            if not all([chosen_first_name, chosen_last_name, chosen_class]):
                render_template('admin_templates/teacher_modification.html', teachers=teachers_dict, classes=classes, 
                           classes_dict=classes_dict, chosen_teacher=chosen_teacher, 
                           error_message=error_message, success_message=success_message)
        
            # Modify the teacher in the database
            try:
                teacher.first_name = chosen_first_name
                teacher.last_name = chosen_last_name
                
                classes = Class.query.all()
                for class_ in classes:
                    if class_.id in chosen_classes:
                        class_.head_teacher_id = teacher.id
                        db.session.add(class_)
                
                db.session.commit()
                print('Teacher modified successfully')  
                return redirect(url_for('admin_dashboard.teacher_modification'))
                
            except Exception as e:
                db.session.rollback()
                error_message=f'An error occurred: {e}'
    
    return render_template('admin_templates/teacher_modification.html', teachers=teachers_dict, classes=classes, 
                           classes_dict=classes_dict, chosen_teacher=chosen_teacher, 
                           error_message=error_message, success_message=success_message)