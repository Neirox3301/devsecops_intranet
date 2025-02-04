from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()

# Modèle pour l'utilisateur
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('teacher', 'student', name='role_enum'), nullable=False)  # Définir le type ENUM

    # Relations avec les autres tables
    teacher = db.relationship('Teacher', backref='user', uselist=False)  # Un utilisateur peut être un enseignant
    student = db.relationship('Student', backref='user', uselist=False)  # Un utilisateur peut être un élève
    
    @property
    def is_active(self):
        return True  # Tu peux ajouter une logique ici si tu veux plus de contrôle
    


# Modèle pour la matière
class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    # Relations avec les autres tables
    teacher_subjects = db.relationship('TeacherSubject', backref='subject')
    grades = db.relationship('Grade', backref='subject')
    teacher_classes = db.relationship('TeacherClass', backref='subject')


# Modèle pour l'enseignant
class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relations avec les autres tables
    classes = db.relationship('TeacherClass', backref='teacher')
    subjects = db.relationship('TeacherSubject', backref='teacher')
    head_class = db.relationship('Class', backref='head_teacher', uselist=False)


# Modèle pour la classe
class Class(db.Model):
    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(20), nullable=False)
    head_teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True)

    # Relations avec les autres tables
    students = db.relationship('Student', backref='class')
    teacher_classes = db.relationship('TeacherClass', backref='class')


# Modèle pour l'élève
class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)

    # Relations avec les autres tables
    grades = db.relationship('Grade', backref='student')


# Modèle pour les notes
class Grade(db.Model):
    __tablename__ = 'grades'

    grade = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), primary_key=True)


# Modèle pour la liaison entre les enseignants et les matières
class TeacherSubject(db.Model):
    __tablename__ = 'teacher_subjects'

    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), primary_key=True)


# Modèle pour la liaison entre les enseignants, les matières et les classes
class TeacherClass(db.Model):
    __tablename__ = 'teacher_classes'

    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), primary_key=True)
