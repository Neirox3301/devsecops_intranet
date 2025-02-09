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
    if user:
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
            classes = Class.query.filter_by(head_teacher_id=teacher.id).all()
            teacher_classes = TeacherClass.query.filter_by(teacher_id=teacher.id).all()
            teacher_subjects = TeacherSubject.query.filter_by(teacher_id=teacher.id).all()
            
            for class_ in classes:
                class_.head_teacher_id = None
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


# Create a user
def create_user(username: str, password: str, confirmed_password: str, role: str) -> tuple[bool | User, str]:
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    # Clear the db session from a previous unfinished user creation
    last_user = User.query.order_by(User.id.desc()).first()
    delete_user_if_no_associated_account(last_user)
    
    # Check if all the fields are filled
    if not all([username, password, confirmed_password, role]):
        return False, 'Please fill all the fields'
    
    # Check in the User table to see if the username is already taken
    if User.query.filter_by(username=username).first():
        return False, 'Username already taken'
     
    # Check if the password and the confirm password are the same
    if password != confirmed_password:
        return False, 'Passwords do not match'

    # Clear the db session
    db.session.rollback()
    
    # Create the user
    user = None
    try:
        pwhash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        user = User(username=username, password=pwhash, role=role)
        db.session.add(user)
        db.session.commit()
        return user, 'User created successfully'
    except:
        db.session.rollback()
        delete_user_if_no_associated_account(user)
        return False, 'An error occurred'
    

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
    users = User.query.all()
    users_dict = [{'id': user.id, 'username': user.username, 'role': user.role} for user in users]
    
    students = Student.query.all()
    students_dict = [{'id': student.id, 'first_name': student.first_name, 'last_name': student.last_name, 'class_id': int(student.class_id), 'username': [user['username'] for user in users_dict if user['id'] == student.user_id][0]} for student in students]
    
    classes = Class.query.all()
    classes_dict = [{'id': class_.id, 'name': class_.class_name} for class_ in classes]
    classes = {class_.id: class_.class_name for class_ in classes}
    
    # Initialize the variables
    new_student = False
    chosen_student = None

    user_dict = None
    student_id = None
    new_chosen_student_id = None
    
    chosen_first_name = None
    chosen_last_name = None
    chosen_class = None
    
    error_message = None
    success_message = None
    
    # Once a student is chosen, display the form with the student's information
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create' or action == 'create_save':
            new_student = True
        else:
            # Check if a student is chosen
            chosen_student_id = request.form.get('chosen_student_id')
            if chosen_student_id:
                chosen_student_id = int(chosen_student_id)
                chosen_student = [student for student in students_dict if student['id'] == chosen_student_id][0]
            
            # Check if the information form (second form) is submitted
            new_chosen_student_id = request.form.get('new_chosen_student_id')
            if not new_chosen_student_id:
                return render_template('admin_templates/student_modification.html', user=user_dict, students=students_dict, classes=classes, 
                                    classes_dict=classes_dict, chosen_student=chosen_student, new_student=new_student,
                                    error_message=error_message, success_message=success_message)
        
            # Get the chosen student from the database
            student_id = int(request.form.get('new_chosen_student_id'))
            student = Student.query.get(student_id)
            if not student:
                error_message = 'Student not found'
                return render_template('admin_templates/student_modification.html', user=user_dict, students=students_dict, classes=classes, 
                                    classes_dict=classes_dict, chosen_student=chosen_student, new_student=new_student,
                                    error_message=error_message, success_message=success_message)
            
        # Get the information from the form
        username = request.form.get('username')
        password = request.form.get('password')
        confirmed_password = request.form.get('confirmed_password')
        
        chosen_first_name = request.form.get('first_name')
        chosen_last_name = request.form.get('last_name')
        chosen_class = request.form.get('selected_class')
        chosen_class = int(chosen_class) if chosen_class else None
                
        match action:
            case 'create_save':
                # Check if all the fields are filled
                if not all([chosen_first_name, chosen_last_name, chosen_class]):
                    render_template('admin_templates/student_modification.html', user=user_dict, students=students_dict, classes=classes, 
                            classes_dict=classes_dict, chosen_student=chosen_student, new_student=new_student,
                            error_message='Please fill all the fields', success_message=success_message)
                
                user_created, message = create_user(username, password, confirmed_password, 'student')
                
                
                if user_created:
                    try:
                        student = Student(first_name=chosen_first_name, last_name=chosen_last_name, class_id=chosen_class, user_id=user_created.id)
                        db.session.add(student)
                        db.session.commit()
                        return redirect(url_for('admin_dashboard.student_modification'))
                    except Exception as e:
                        db.session.rollback()
                        error_message=f'An error occurred: {e}'
                else:
                    error_message = message
                    return render_template('admin_templates/student_modification.html', user=user_dict, students=students_dict, classes=classes, 
                                    classes_dict=classes_dict, chosen_student=chosen_student, new_student=new_student,
                                    error_message=error_message, success_message=success_message)
            
            
            case 'display':
                render_template('admin_templates/student_modification.html', user=user_dict, students=students_dict, classes=classes, 
                    classes_dict=classes_dict, chosen_student=chosen_student, new_student=new_student,
                    error_message=error_message, success_message=success_message)
            
            
            case 'modify':
                try:
                    student.first_name = chosen_first_name
                    student.last_name = chosen_last_name
                    student.class_id = chosen_class
                    db.session.commit()
                    return redirect(url_for('admin_dashboard.student_modification'))
                except Exception as e:
                    db.session.rollback()
                    error_message=f'An error occurred: {e}'
                    
            
            case 'delete':
                try:
                    student_deleted = delete_student(student_id)
                    if student_deleted:
                        success_message='Student deleted successfully'
                        return redirect(url_for('admin_dashboard.student_modification'))
                    
                    else:
                        error_message='An error occurred while deleting the student'
                        return render_template('admin_templates/student_modification.html', user=user_dict, students=students_dict, classes=classes, 
                                    classes_dict=classes_dict, chosen_student=chosen_student, new_student=new_student,
                                    error_message=error_message, success_message=success_message)
                except Exception as e:
                    db.session.rollback()
                    error_message=f'An error occurred: {e}'
        
    
    return render_template('admin_templates/student_modification.html', user=user_dict, students=students_dict, classes=classes, 
                           classes_dict=classes_dict, chosen_student=chosen_student, new_student=new_student,
                           error_message=error_message, success_message=success_message)



@admin_dashboard_blueprint.route('/admin_dashboard/teacher_modification', methods=['GET', 'POST'])
@login_required
def teacher_modification():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    # Get all the data from the database
    users = User.query.all()
    users_dict = [{'id': user.id, 'username': user.username, 'role': user.role} for user in users]
    
    subjects = Subject.query.all()
    subjects_dict = [{'id': subject.id, 'name': subject.name} for subject in subjects]
    
    classes = Class.query.all()
    classes_dict = [{'id': class_.id, 'name': class_.class_name, 'head_teacher_id': class_.head_teacher_id} for class_ in classes]
    
    teacher_subjects = TeacherSubject.query.all()
    teacher_subjects_dict = [{'teacher_id': teacher_subject.teacher_id, 'subject_id': teacher_subject.subject_id} for teacher_subject in teacher_subjects]
    
    teacher_classes = TeacherClass.query.all()
    teacher_classes_dict = [{'teacher_id': teacher_class.teacher_id, 'class_id': teacher_class.class_id, 'subject_id': teacher_class.subject_id} for teacher_class in teacher_classes]    
    
    teachers = Teacher.query.all()
    teachers_dict = [{'id': teacher.id, 
                      'first_name': teacher.first_name, 
                      'last_name': teacher.last_name,
                      'username': [user['username'] for user in users_dict if user['id'] == teacher.user_id][0],
                      'head_teacher_classes': [class_['id'] for class_ in classes_dict if class_['head_teacher_id'] == teacher.id],
                      'subjects': [subject['subject_id'] for subject in teacher_subjects_dict if subject['teacher_id'] == teacher.id]
                     } for teacher in teachers]
    
    classes_subjects_dict = {0: []}
    
    # Initialize the variables
    new_teacher = False
    chosen_teacher = None

    user_dict = None
    teacher_id = None
    new_chosen_teacher_id = None
    
    chosen_first_name = None
    chosen_last_name = None
    
    error_message = None
    success_message = None
    
    # Once a teacher is chosen, display the form with the teacher's information
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create' or action == 'create_save':
            new_teacher = True
        else:
            # Check if a teacher is chosen
            chosen_teacher_id = request.form.get('chosen_teacher_id')
            if chosen_teacher_id:
                chosen_teacher_id = int(chosen_teacher_id)
                chosen_teacher = [teacher for teacher in teachers_dict if teacher['id'] == chosen_teacher_id][0]
                classes_subjects_dict = {class_['id']: [subject['subject_id'] if subject['class_id'] == class_['id'] and subject['teacher_id'] == chosen_teacher['id'] else 0 for subject in teacher_classes_dict] for class_ in classes_dict}

            
            # Check if the information form (second form) is submitted
            new_chosen_teacher_id = request.form.get('new_chosen_teacher_id')
            if not new_chosen_teacher_id:
                return render_template('admin_templates/teacher_modification.html', user=user_dict, teachers=teachers_dict, classes=classes, 
                                    classes_dict=classes_dict, subjects=subjects_dict, class_subjects=classes_subjects_dict, chosen_teacher=chosen_teacher, new_teacher=new_teacher,
                                    error_message='error_message', success_message=success_message)
        
            # Get the chosen teacher from the database
            teacher_id = int(request.form.get('new_chosen_teacher_id'))
            teacher = Teacher.query.get(teacher_id)
            if not teacher:
                error_message = 'Teacher not found'
                return render_template('admin_templates/teacher_modification.html', user=user_dict, teachers=teachers_dict, classes=classes, 
                                    classes_dict=classes_dict, subjects=subjects_dict, class_subjects=classes_subjects_dict, chosen_teacher=chosen_teacher, new_teacher=new_teacher,
                                    error_message=error_message, success_message=success_message)
            
        # Get the information from the form
        username = request.form.get('username')
        password = request.form.get('password')
        confirmed_password = request.form.get('confirmed_password')
        
        chosen_first_name = request.form.get('first_name')
        chosen_last_name = request.form.get('last_name')
        head_teacher_classes = request.form.getlist('head_teacher_classes')
        teacher_subjects = request.form.getlist('teacher_subjects')
        
        
        class_subjects = {}
        for key in request.form:
            if '|' in key:  # Détecter les entrées des classes (ex: "class_id|subject_id")
                class_id, subject_id = key.split('|')
                if class_id not in class_subjects:
                    class_subjects[class_id] = []
                class_subjects[class_id].append(subject_id)


        
        print((username, password, confirmed_password, chosen_first_name, chosen_last_name, head_teacher_classes, teacher_subjects, teacher_classes))
        print(f'ACTION: {action}')
        match action:
            case 'create_save':
                # Check if all the fields are filled
                if not all([chosen_first_name, chosen_last_name]):
                    return render_template('admin_templates/teacher_modification.html', user=user_dict, teachers=teachers_dict, classes=classes, 
                                    classes_dict=classes_dict, subjects=subjects_dict, class_subjects=classes_subjects_dict, chosen_teacher=chosen_teacher, new_teacher=new_teacher,
                                    error_message=error_message, success_message=success_message)
                
                user_created, message = create_user(username, password, confirmed_password, 'teacher')
                if user_created:
                    try:
                        teacher = Teacher(first_name=chosen_first_name, last_name=chosen_last_name, user_id=user_created.id)
                        db.session.add(teacher)
                        db.session.flush()
                        
                        teacher_subjects_objects = [
                            TeacherSubject(teacher_id=teacher.id, subject_id=subject_id) 
                            for subject_id in teacher_subjects
                        ]
                        
                        teacher_classes = []
                        for class_id in class_subjects:
                            for subject_id in class_subjects[class_id]:
                                teacher_classes.append(
                                    TeacherClass(teacher_id=teacher.id, class_id=class_id, subject_id=subject_id)
                                )
                        
                        db.session.add_all(teacher_subjects_objects)
                        db.session.add_all(teacher_classes)
                        
                        db.session.commit()
                        return redirect(url_for('admin_dashboard.teacher_modification'))
                    except Exception as e:
                        db.session.rollback()
                        error_message=f'An error occurred: {e}'
                else:
                    error_message = message
                    return render_template('admin_templates/teacher_modification.html', user=user_dict, teachers=teachers_dict, classes=classes, 
                                    classes_dict=classes_dict, subjects=subjects_dict, class_subjects=classes_subjects_dict, chosen_teacher=chosen_teacher, new_teacher=new_teacher,
                                    error_message=error_message, success_message=success_message)
            
            
            case 'display':
                classes_subjects_dict = {class_['id']: [subject['subject_id'] for subject in teacher_classes_dict if subject['class_id'] == class_['id'] and subject['teacher_id'] == teacher.id] for class_ in classes_dict}
                print(f'Classes subjects dict 2: {classes_subjects_dict}')
                return render_template('admin_templates/teacher_modification.html', user=user_dict, teachers=teachers_dict, classes=classes, 
                                    classes_dict=classes_dict, subjects=subjects_dict, class_subjects=classes_subjects_dict, chosen_teacher=chosen_teacher, new_teacher=new_teacher,
                                    error_message=error_message, success_message=success_message)
            
            
            case 'modify':
                try:
                    teacher.first_name = chosen_first_name
                    teacher.last_name = chosen_last_name                    
                    head_teacher_classes = list(map(int, head_teacher_classes))
                    
                    # Update the head teacher classes
                    for class_ in classes:
                        if class_.id in head_teacher_classes:
                            class_.head_teacher_id = teacher.id
                        elif class_.head_teacher_id == teacher.id:
                            class_.head_teacher_id = None
                    
                    print("Test")
                    db.session.commit()
                    return redirect(url_for('admin_dashboard.teacher_modification'))
                except Exception as e:
                    db.session.rollback()
                    error_message=f'An error occurred: {e}'
                    
            
            case 'delete':
                try:
                    teacher_deleted = delete_teacher(teacher_id)
                    if teacher_deleted:
                        success_message='Teacher deleted successfully'
                        return redirect(url_for('admin_dashboard.teacher_modification'))
                    
                    else:
                        error_message='An error occurred while deleting the teacher'
                        return render_template('admin_templates/teacher_modification.html', user=user_dict, teachers=teachers_dict, classes=classes, 
                                    classes_dict=classes_dict, subjects=subjects_dict, class_subjects=classes_subjects_dict, chosen_teacher=chosen_teacher, new_teacher=new_teacher,
                                    error_message=error_message, success_message=success_message)
                except Exception as e:
                    db.session.rollback()
                    error_message=f'An error occurred: {e}'
        
    
    return render_template('admin_templates/teacher_modification.html', user=user_dict, teachers=teachers_dict, classes=classes, 
                                    classes_dict=classes_dict, subjects=subjects_dict, class_subjects=classes_subjects_dict, chosen_teacher=chosen_teacher, new_teacher=new_teacher,
                                    error_message=error_message, success_message=success_message)









































































# def member_modification(role, **kwargs):
#     if current_user.role != 'admin':
#         return redirect(url_for('auth.login'))
    
#     members_dict = []
#     match role:
#         case 'student':
#             redirect_url = 'admin_dashboard.student_modification'
#             members = Student.query.all()
#             members_dict = [{'id': member.id, 'first_name': member.first_name, 
#                              'last_name': member.last_name, 
#                              'class_id': member.class_id} for member in members]
        
#         case 'teacher':
#             redirect_url = 'admin_dashboard.teacher_modification'
#             classes = Class.query.all()
#             members = Teacher.query.all()
#             members_dict = [{'id': member.id, 'first_name': member.first_name, 
#                              'last_name': member.last_name, 
#                              'head_teacher_classes': [class_.id for class_ in classes if class_.head_teacher_id == member.id]} for member in members]
            
#         case 'admin':
#             redirect_url = 'admin_dashboard.admin_modification'
#             members = Admin.query.all()
#             members_dict = [{'id': member.id, 
#                              'first_name': member.first_name, 
#                              'last_name': member.last_name} for member in members]

    
#     # Initialize the variables
#     chosen_member = None
#     new_member = False
    
#     user_dict = None
#     member_id = None
#     new_chosen_member_id = None
    
#     chosen_first_name = None
#     chosen_last_name = None
#     chosen_class = None
    
#     error_message = None
#     success_message = None
    
#     # Once a member is chosen or need to be created, display the form with the member's information
#     if request.method == 'POST':
#         action = request.form.get('action')
        
#         if action == 'create':
#             new_member = True
#         else:
#             # Check if a member is chosen
#             chosen_member_id = request.form.get('chosen_member_id')
#             if chosen_member_id:
#                 chosen_member_id = int(chosen_member_id)
#                 chosen_member = [member for member in members_dict if member['id'] == chosen_member_id][0]
            
#             # Check if the information form is submitted
#             new_chosen_member_id = request.form.get('new_chosen_member_id')
#             print(f'New chosen member id: {new_chosen_member_id}')
#             if not new_chosen_member_id:
#                 return render_template(f'{redirect_url}', user=user_dict, members=members_dict, 
#                                     chosen_member=chosen_member, new_member=new_member,
#                                     error_message=error_message, success_message=success_message)
        
#             # Get the chosen member from the database
#             member_id = int(request.form.get('new_chosen_member_id'))
#             member = None
#             match role:
#                 case 'student':
#                     member = Student.query.get(member_id)
#                 case 'teacher':
#                     member = Teacher.query.get(member_id)
#                 case 'admin':
#                     member = Admin.query.get(member_id)
            
#             if not member:
#                 error_message = 'Member not found'
#                 return render_template(f'{redirect_url}', user=user_dict, members=members_dict, 
#                                     chosen_member=chosen_member, new_member=new_member,
#                                     error_message=error_message, success_message=success_message)
            
#         # Get the information from the form
#         username = request.form.get('username')
#         password = request.form.get('password')
#         confirmed_password = request.form.get('confirmed_password')
        
#         chosen_first_name = request.form.get('first_name')
#         chosen_last_name = request.form.get('last_name')
#         chosen_class = request.form.get('selected_class')
#         chosen_class = int(chosen_class) if chosen_class else None
        
        
        
#         match role:
#             case 'create':
#                 # Check if all the fields are filled
#                 if not all([chosen_first_name, chosen_last_name, chosen_class]):
#                     render_template(f'{redirect_url}', user=user_dict, members=members_dict, 
#                             chosen_member=chosen_member, new_member=new_member,
#                             error_message='Please fill all the fields', success_message=success_message)
                    
                    
                    
                    
#         class_subjects = {}
#         for key in request.form:
#             if '|' in key:  # Détecter les entrées des classes (ex: "class_id|subject_id")
#                 class_id, subject_id = key.split('|')
#                 if class_id not in class_subjects:
#                     class_subjects[class_id] = []
#                 class_subjects[class_id].append(subject_id)