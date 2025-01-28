from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__)

config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'utilisateurs',
    'raise_on_warnings': True
}

@app.route('/', methods=['GET', 'POST'])
def login():
    message = ""
    if request.method == 'POST':
        nom = request.form.get('nom').strip()
        prenom = request.form.get('prenom').strip()

        if nom and prenom:
            try:
                # Connexion à la base de données
                conn = mysql.connector.connect(**config)
                cursor = conn.cursor(dictionary=True)

                # Requête pour vérifier l'utilisateur
                query = "SELECT status FROM etudiants WHERE nom = %s AND prenom = %s"
                cursor.execute(query, (nom, prenom))
                result = cursor.fetchone()

                if result:
                    status = result['status']
                    if status:
                        message = f"Bienvenue, Professeur {nom} {prenom}!"
                    else:
                        message = f"Bienvenue, Étudiant {nom} {prenom}!"
                else:
                    message = "Utilisateur non trouvé dans la base de données."

            except mysql.connector.Error as err:
                message = f"Erreur de connexion à la base de données: {err}"

            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
        else:
            message = "Veuillez remplir tous les champs."

    return render_template('index.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
