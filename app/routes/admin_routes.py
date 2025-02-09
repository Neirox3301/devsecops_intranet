from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from models import User, Admin, Student, Teacher, Class, TeacherClass, TeacherSubject, Grade, Subject, db

admin_dashboard_blueprint = Blueprint('admin_dashboard', __name__)


# ---- Routes principales ----

# --- Gestion des Étudiants ---
@admin_dashboard_blueprint.route('/admin_dashboard/student_modification', methods=['GET', 'POST'])
@login_required
def student_modification():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))

    context = get_common_context(Student, 'admin_templates/student_modification.html')

    if request.method == 'POST':
        return handle_post_request(request, context, create_student, modify_student, delete_student)

    return render_page(context)

def create_student(request, context):
    """Crée un étudiant."""
    first_name, last_name, class_id = request.form.get('first_name'), request.form.get('last_name'), request.form.get('selected_class')
    username, password, confirmed_password = request.form.get('username'), request.form.get('password'), request.form.get('confirmed_password')

    if not all([first_name, last_name, class_id]):
        context['error_message'] = "Tous les champs doivent être remplis."
        return render_page(context)

    user, msg = create_user(username, password, confirmed_password, 'student')
    if not user:
        context['error_message'] = msg
        return render_page(context)

    student = Student(first_name=first_name, last_name=last_name, class_id=int(class_id), user_id=user.id)
    db.session.add(student)
    db.session.commit()
    return redirect(url_for('admin_dashboard.student_modification'))

def modify_student(request, context):
    """Modifie un étudiant."""
    student_id = request.form.get('new_chosen_student_id')
    student = Student.query.get(student_id)
    if not student:
        context['error_message'] = "Étudiant introuvable."
        return render_page(context)

    student.first_name = request.form.get('first_name')
    student.last_name = request.form.get('last_name')
    student.class_id = int(request.form.get('selected_class'))

    user = User.query.get(student.user_id)
    user.username = request.form.get('username')
    user.password = generate_password_hash(request.form.get('password')) if request.form.get('password') else user.password

    db.session.commit()
    return redirect(url_for('admin_dashboard.student_modification'))

# --- Gestion des Enseignants ---
@admin_dashboard_blueprint.route('/admin_dashboard/teacher_modification', methods=['GET', 'POST'])
@login_required
def teacher_modification():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))

    context = get_common_context(Teacher, 'admin_templates/teacher_modification.html')

    if request.method == 'POST':
        return handle_post_request(request, context, create_teacher, modify_teacher, delete_teacher)

    return render_page(context)

def create_teacher(request, context):
    """Crée un enseignant."""
    first_name, last_name = request.form.get('first_name'), request.form.get('last_name')
    username, password, confirmed_password = request.form.get('username'), request.form.get('password'), request.form.get('confirmed_password')

    if not all([first_name, last_name]):
        context['error_message'] = "Tous les champs doivent être remplis."
        return render_page(context)

    user, msg = create_user(username, password, confirmed_password, 'teacher')
    if not user:
        context['error_message'] = msg
        return render_page(context)

    teacher = Teacher(first_name=first_name, last_name=last_name, user_id=user.id)
    db.session.add(teacher)
    db.session.commit()
    
    
    # Mise à jour des classes dont il est professeur principal
    head_teacher_classes = request.form.getlist('head_teacher_classes')
    for class_ in Class.query.all():
        class_.head_teacher_id = teacher.id if str(class_.id) in head_teacher_classes else None

    # Mise à jour des matières enseignées
    selected_subjects = request.form.getlist('teacher_subjects')
    TeacherSubject.query.filter_by(teacher_id=teacher.id).delete()
    db.session.add_all([TeacherSubject(teacher_id=teacher.id, subject_id=int(subj_id)) for subj_id in selected_subjects])

    # Mise à jour des matières enseignées par classe
    TeacherClass.query.filter_by(teacher_id=teacher.id).delete()
    for key in request.form:
        if "|" in key:  # Exemple : "class_id|subject_id"
            class_id, subject_id = key.split("|")
            db.session.add(TeacherClass(teacher_id=teacher.id, class_id=int(class_id), subject_id=int(subject_id)))
    
    db.session.commit()
    return redirect(url_for('admin_dashboard.teacher_modification'))

def modify_teacher(request, context):
    """Modifie un enseignant et met à jour ses matières et classes."""
    teacher_id = request.form.get('new_chosen_teacher_id')
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        context['error_message'] = "Enseignant introuvable."
        return render_page(context)

    teacher.first_name = request.form.get('first_name')
    teacher.last_name = request.form.get('last_name')

    # Mise à jour des classes dont il est professeur principal
    head_teacher_classes = request.form.getlist('head_teacher_classes')
    for class_ in Class.query.all():
        class_.head_teacher_id = teacher.id if str(class_.id) in head_teacher_classes else None

    # Mise à jour des matières enseignées
    selected_subjects = request.form.getlist('teacher_subjects')
    TeacherSubject.query.filter_by(teacher_id=teacher.id).delete()
    db.session.add_all([TeacherSubject(teacher_id=teacher.id, subject_id=int(subj_id)) for subj_id in selected_subjects])

    # Mise à jour des matières enseignées par classe
    TeacherClass.query.filter_by(teacher_id=teacher.id).delete()
    for key in request.form:
        if "|" in key:  # Exemple : "class_id|subject_id"
            class_id, subject_id = key.split("|")
            db.session.add(TeacherClass(teacher_id=teacher.id, class_id=int(class_id), subject_id=int(subject_id)))

    user = User.query.get(teacher.user_id)
    user.username = request.form.get('username')
    user.password = generate_password_hash(request.form.get('password')) if request.form.get('password') else user.password


    db.session.commit()
    return redirect(url_for('admin_dashboard.teacher_modification'))

# --- Gestion des Administrateurs ---
@admin_dashboard_blueprint.route('/admin_dashboard/admin_modification', methods=['GET', 'POST'])
@login_required
def admin_modification():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))

    context = get_common_context(Admin, 'admin_templates/admin_modification.html')

    if request.method == 'POST':
        return handle_post_request(request, context, create_admin, modify_admin, delete_admin)

    return render_page(context)

def create_admin(request, context):
    """Crée un administrateur."""
    first_name, last_name = request.form.get('first_name'), request.form.get('last_name')
    username, password, confirmed_password = request.form.get('username'), request.form.get('password'), request.form.get('confirmed_password')

    if not all([first_name, last_name]):
        context['error_message'] = "Tous les champs doivent être remplis."
        return render_page(context)

    user, msg = create_user(username, password, confirmed_password, 'admin')
    if not user:
        context['error_message'] = msg
        return render_page(context)

    admin = Admin(first_name=first_name, last_name=last_name, user_id=user.id)
    db.session.add(admin)
    db.session.commit()
    return redirect(url_for('admin_dashboard.admin_modification'))

def modify_admin(request, context):
    """Modifie un administrateur."""
    admin_id = request.form.get('new_chosen_admin_id')
    admin = Admin.query.get(admin_id)
    if not admin:
        context['error_message'] = "Administrateur introuvable."
        return render_page(context)

    admin.first_name = request.form.get('first_name')
    admin.last_name = request.form.get('last_name')
    
    user = User.query.get(admin.user_id)
    user.username = request.form.get('username')
    user.password = generate_password_hash(request.form.get('password')) if request.form.get('password') else user.password

    db.session.commit()
    return redirect(url_for('admin_dashboard.admin_modification'))



# --- Fonctions Utilitaires ---
def get_common_context(model, template):
    """Récupère les utilisateurs, classes et entités spécifiques (students, teachers, admins)."""
    users = User.query.all()
    users_dict = {user.id: user.username for user in users}

    entities = model.query.all()
    entities_dict = [
        {
            'id': entity.id,
            'first_name': entity.first_name,
            'last_name': entity.last_name,
            'username': users_dict.get(entity.user_id, ''),
            'class_id': entity.class_id if model == Student else None,
            'head_teacher_classes': [class_.id for class_ in Class.query.filter_by(head_teacher_id=entity.id)],
            'subjects': [ts.subject_id for ts in TeacherSubject.query.filter_by(teacher_id=entity.id)]
        }
        for entity in entities
    ]

    classes = Class.query.all()
    classes_dict = {class_.id: class_.class_name for class_ in classes}

    subjects = Subject.query.all()
    subjects_dict = {subject.id: subject.name for subject in subjects}

    teacher_classes = TeacherClass.query.all()
    teacher_classes_dict = {}
    for tc in teacher_classes:
        teacher_classes_dict.setdefault((tc.teacher_id, tc.class_id), []).append(tc.subject_id)

    return {
        'users_dict': users_dict,
        'entities_dict': entities_dict,
        'classes_dict': classes_dict,
        'subjects_dict': subjects_dict,
        'teacher_classes_dict': teacher_classes_dict,
        'chosen_entity': None,
        'new_entity': False,
        'error_message': None,
        'success_message': None,
        'template': template
    }

def render_page(context):
    """Rend le template avec le contexte."""
    return render_template(context['template'], **context)

def handle_post_request(request, context, create_func, modify_func, delete_func):
    """Gère les actions POST pour modification, création et suppression."""
    action = request.form.get('action')
    chosen_entity_id = request.form.get('chosen_entity_id')

    if action in ['create', 'create_save']:
        context['new_entity'] = True
    else:
        context['chosen_entity'] = next((entity for entity in context['entities_dict'] if str(entity['id']) == chosen_entity_id), None)
    
    if action == 'create_save':
        return create_func(request, context)
    elif action == 'modify':
        return modify_func(request, context)
    elif action == 'delete':
        return delete_func(request, context)
    
    return render_page(context)

def create_user(username, password, confirmed_password, role):
    """Crée un utilisateur en vérifiant les contraintes de validation."""
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))

    if not all([username, password, confirmed_password, role]):
        return False, 'Veuillez remplir tous les champs.'

    if User.query.filter_by(username=username).first():
        return False, 'Nom d\'utilisateur déjà pris.'

    if password != confirmed_password:
        return False, 'Les mots de passe ne correspondent pas.'

    db.session.rollback()  # Nettoyer la session au cas où

    try:
        user = User(username=username, password=generate_password_hash(password), role=role)
        db.session.add(user)
        db.session.commit()
        return user, 'Utilisateur créé avec succès.'
    except Exception:
        db.session.rollback()
        return False, 'Une erreur est survenue lors de la création de l\'utilisateur.'


def delete_user_if_no_associated_account(user):
    """Supprime un utilisateur s'il n'a pas de compte associé (étudiant, enseignant, admin)."""
    if user and not any([
        Student.query.filter_by(user_id=user.id).first(),
        Teacher.query.filter_by(user_id=user.id).first(),
        Admin.query.filter_by(user_id=user.id).first()
    ]):
        db.session.delete(user)
        db.session.commit()


def delete_entity(model, entity_id):
    """Supprime une entité (Admin, Student, Teacher) et son utilisateur associé si possible."""
    entity = model.query.get(entity_id)
    if entity:
        try:
            user = User.query.get(entity.user_id)
            db.session.delete(entity)
            if user:
                delete_user_if_no_associated_account(user)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    return False


def delete_student(student_id):
    """Supprime un étudiant, ses notes et son utilisateur si applicable."""
    student = Student.query.get(student_id)
    if student:
        try:
            Grade.query.filter_by(student_id=student.id).delete()
            return delete_entity(Student, student_id)
        except Exception:
            db.session.rollback()
            return False
    return False


def delete_teacher(teacher_id):
    """Supprime un enseignant et dissocie les classes dont il est responsable."""
    teacher = Teacher.query.get(teacher_id)
    if teacher:
        try:
            # Dissocier les classes dont il est professeur principal
            Class.query.filter(Class.head_teacher_id == teacher.id).update({'head_teacher_id': None})
            TeacherClass.query.filter_by(teacher_id=teacher.id).delete()
            TeacherSubject.query.filter_by(teacher_id=teacher.id).delete()
            return delete_entity(Teacher, teacher_id)
        except Exception:
            db.session.rollback()
            return False
    return False


def delete_admin(admin_id):
    """Supprime un administrateur et son utilisateur associé."""
    return delete_entity(Admin, admin_id)


