CREATE DATABASE IF NOT EXISTS utilisateurs;
USE utilisateurs;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    notes_matiere1 DECIMAL(5,2) DEFAULT NULL,
    notes_matiere2 DECIMAL(5,2) DEFAULT NULL,
    notes_matiere3 DECIMAL(5,2) DEFAULT NULL,
    notes_matiere4 DECIMAL(5,2) DEFAULT NULL,
    notes_matiere5 DECIMAL(5,2) DEFAULT NULL,
    password VARCHAR(255) NOT NULL,
    status BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO etudiants (nom, prenom, notes_matiere1, notes_matiere2, notes_matiere3, notes_matiere4, notes_matiere5, password, status)
VALUES
    ('Dupont', 'Jean', 15.50, 14.00, 13.00, 16.00, 17.00, 'password123', FALSE),
    ('Pierre', 'Prof', NULL, NULL, NULL, NULL, NULL, 'securepassword', TRUE);
