import mysql.connector

config = {
    'user': 'root',
    'password': 'admin',
    'host': 'localhost',
    'database': 'academis'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**config)
        return conn
    except mysql.connector.Error as err:
        print(f"Erreur de connexion à MySQL: {err}")
        return None
