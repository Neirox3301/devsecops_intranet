CREATE DATABASE IF NOT EXISTS utilisateurs;
USE utilisateurs;

CREATE TABLE IF NOT EXISTS etudiants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    status BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO etudiants (nom, prenom, password, status) VALUES
('Dupont', 'Jean', 'password123', FALSE),
('Pierre', 'Prof', 'securepassword', TRUE);