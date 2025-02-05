from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user

from models import User, Admin, Student, Teacher, Class, db

admin_dashboard_blueprint = Blueprint('admin_dashboard', __name__)



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
        user = User(username=chosen_username, password=chosen_password, role=chosen_role)
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
    
    return render_template('admin_templates/teacher_creation.html', classes=classes, error_message=error_message)


# Teacher creation function
@admin_dashboard_blueprint.route('/admin_dashboard/create_teacher', methods=['GET', 'POST'])
@login_required
def create_teacher():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    return redirect(url_for('admin_dashboard.teacher_creation_form'))



# Admin creation form
@admin_dashboard_blueprint.route('/admin_dashboard/admin_creation', methods=['GET', 'POST'])
@login_required
def admin_creation(error_message=None):
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    return render_template('admin_templates/admin_creation.html', error_message=error_message)

# Admin creation function
@admin_dashboard_blueprint.route('/admin_dashboard/create_admin', methods=['GET', 'POST'])
@login_required
def create_admin():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    return redirect(url_for('admin_dashboard.admin_creation'))
