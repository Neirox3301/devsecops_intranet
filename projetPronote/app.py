from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

config = {
    'user': 'root',
    'password': 'admin',
    'host': 'localhost',
    'database': 'utilisateurs'
}

@app.route('/')
def home():
    return render_template('index.html', message="")

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/process', methods=['POST'])
def process():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return render_template('index.html', message="Veuillez remplir tous les champs.")

    conn = None

    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT CONCAT(LEFT(prenom, 1), nom) AS generated_username, status
        FROM users
        WHERE password = %s
        """
        
        cursor.execute(query, (password,))
        result = cursor.fetchone()

        if result:
            expected_username = result['generated_username']
            
            if username == expected_username:
                return redirect(url_for('dashboard'))
            else:
                message = "Nom d'utilisateur incorrect."
        else:
            message = "Mot de passe incorrect ou utilisateur non trouvé."

    except mysql.connector.Error as e:
        message = f"Erreur de connexion à la base de données : {e}"

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return render_template('index.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
