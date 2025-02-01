-- Suppression des tables si elles existent déjà
DROP TABLE IF EXISTS teacher_subjects;
DROP TABLE IF EXISTS teacher_classes;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS classes;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS users;

-- Création de la table 'users' pour centraliser l'authentification
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255),
    role ENUM('teacher', 'student') -- 'teacher' pour enseignants, 'student' pour étudiants
);

-- Création de la table 'subjects'
CREATE TABLE subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50)
);

-- Création de la table 'teachers' en liant chaque enseignant à un utilisateur
CREATE TABLE teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    user_id INT,  -- Référence à l'utilisateur
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Création de la table 'classes'
CREATE TABLE classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name_class VARCHAR(20),
    head_teacher_id INT,  -- Référence au professeur principal
    FOREIGN KEY (head_teacher_id) REFERENCES teachers(id)
);

-- Création de la table 'students' en liant chaque élève à un utilisateur
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    user_id INT,  -- Référence à l'utilisateur
    class_id INT,  -- Référence à la classe de l'élève
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

-- Création de la table de liaison 'teacher_subjects'
CREATE TABLE teacher_subjects (
    teacher_id INT,  -- Référence à un professeur
    subject_id INT,  -- Référence à une matière
    PRIMARY KEY (teacher_id, subject_id),
    FOREIGN KEY (teacher_id) REFERENCES teachers(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);


-- Création de la table de liaison 'teacher_classes'
CREATE TABLE teacher_classes (
    teacher_id INT,
    class_id INT,
    PRIMARY KEY (teacher_id, class_id),
    FOREIGN KEY (teacher_id) REFERENCES teachers(id),
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

CREATE TABLE grades (
	grade INT,
    student_id INT,
    subject_id INT,
    PRIMARY KEY (student_id, subject_id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

-- Insérer des utilisateurs pour les enseignants et les élèves
INSERT INTO users (username, password, role) 
VALUES 
('pdupont', 'password123', 'teacher'),
('slemoine', 'password123', 'teacher'),
('jmartin', 'password123', 'teacher'),
('vbertrand', 'password123', 'teacher'),
('jdupont', 'password123', 'student'),
('alemoine', 'password123', 'student'),
('mboucher', 'password123', 'student'),
('cfavre', 'password123', 'student');

-- Insérer des matières
INSERT INTO subjects (name) 
VALUES 
('Français'),
('Mathématiques'),
('Histoire-Géographie'),
('Anglais'),
('Sciences'),
('Éducation Physique et Sportive'),
('Musique'),
('Arts Plastiques');

-- Insérer des enseignants
INSERT INTO teachers (first_name, last_name, user_id) 
VALUES 
('Paul', 'Dupont', 1),  -- Paul Dupont (Français)
('Sophie', 'Lemoine', 2),  -- Sophie Lemoine (Mathématiques)
('Jean', 'Martin', 3),  -- Jean Martin (Histoire-Géographie)
('Valérie', 'Bertrand', 4);  -- Valérie Bertrand (Sciences)

-- Assigner des matières aux enseignants
INSERT INTO teacher_subjects (teacher_id, subject_id) 
VALUES 
(1, 1),  -- Paul Dupont enseigne le Français
(2, 2),  -- Sophie Lemoine enseigne les Mathématiques
(3, 3),  -- Jean Martin enseigne l'Histoire-Géographie
(4, 5);  -- Valérie Bertrand enseigne les Sciences

-- Insérer des classes et assigner un professeur principal
INSERT INTO classes (name_class, head_teacher_id) 
VALUES 
('6e A', 1),  -- Paul Dupont est professeur principal
('6e B', 2),  -- Sophie Lemoine est professeur principal
('6e C', 3),  -- Jean Martin est professeur principal
('6e D', 4);  -- Valérie Bertrand est professeur principal

-- Insérer des élèves et les lier à des utilisateurs et des classes
INSERT INTO students (first_name, last_name, user_id, class_id) 
VALUES 
('Jean', 'Dupont', 5, 1),  -- Jean Dupont (id utilisateur 5) dans la classe 6e A
('Alice', 'Lemoine', 6, 2),  -- Alice Lemoine (id utilisateur 6) dans la classe 6e B
('Martin', 'Boucher', 7, 3),  -- Martin Boucher (id utilisateur 7) dans la classe 6e C
('Claire', 'Favre', 8, 4);  -- Claire Favre (id utilisateur 8) dans la classe 6e D

-- Assigner des professeurs aux classes
INSERT INTO teacher_classes (teacher_id, class_id) 
VALUES 
(1, 1),  -- Paul Dupont enseigne en 6e A
(1, 2),  -- Paul Dupont enseigne aussi en 6e B
(2, 1),  -- Sophie Lemoine enseigne aussi en 6e A
(2, 3),  -- Sophie Lemoine enseigne en 6e C
(3, 3),  -- Jean Martin enseigne en 6e C
(3, 4),  -- Jean Martin enseigne aussi en 6e D
(4, 2),  -- Valérie Bertrand enseigne en 6e B
(4, 4);  -- Valérie Bertrand enseigne aussi en 6e D

-- Insertion des notes pour les élèves
INSERT INTO grades (grade, student_id, subject_id) 
VALUES 
(15, 1, 1),  -- Jean Dupont en Français
(12, 1, 2),  -- Jean Dupont en Mathématiques
(14, 1, 3),  -- Jean Dupont en Histoire-Géographie
(16, 2, 1),  -- Alice Lemoine en Français
(13, 2, 4),  -- Alice Lemoine en Anglais
(17, 2, 5),  -- Alice Lemoine en Sciences
(10, 3, 2),  -- Martin Boucher en Mathématiques
(14, 3, 6),  -- Martin Boucher en EPS
(11, 3, 7),  -- Martin Boucher en Musique
(18, 4, 3),  -- Claire Favre en Histoire-Géographie
(16, 4, 5),  -- Claire Favre en Sciences
(15, 4, 8);  -- Claire Favre en Arts Plastiques

