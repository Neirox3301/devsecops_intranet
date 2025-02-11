import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

def generate_flask_secret_key(url=''):
    """Génère une clé de chiffrement et chiffre la clé secrète Flask."""
    
    print("[*] Génération d'une nouvelle clé de chiffrement...")
    # Générer une clé de chiffrement
    encryption_key = Fernet.generate_key()

    # Sauvegarder la clé de chiffrement dans un fichier sécurisé
    with open(url + ".venv/.flask_secret_key", "wb") as key_file:
        key_file.write(encryption_key)

    print("[+] Clé de chiffrement générée et sauvegardée.")

    # Charger la clé de chiffrement
    with open(url + ".venv/.flask_secret_key", "rb") as key_file:
        encryption_key = key_file.read()

    cipher = Fernet(encryption_key)

    # Charger la clé secrète Flask
    print("[*] Chargement de la clé secrète Flask...")
    load_dotenv(url + ".env")
    flask_secret = os.getenv("FLASK_SECRET_KEY").encode( )
    print("[+] Clé secrète Flask chargée.")
    
    # Chiffrer la clé secrète Flask
    print("[*] Chiffrement de la clé secrète Flask...")
    encrypted_secret = cipher.encrypt(flask_secret)

    # Sauvegarde dans un fichier sécurisé
    with open(url + ".venv/flask_secret.enc", "wb") as secret_file:
        secret_file.write(encrypted_secret)

    print("[+] Clé secrète Flask chiffrée et sauvegardée.")
    

if __name__ == "__main__":
    url = '../'
    generate_flask_secret_key()