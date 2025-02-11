from cryptography.fernet import Fernet

# Générer une clé de chiffrement
encryption_key = Fernet.generate_key()

# Sauvegarder la clé de chiffrement dans un fichier sécurisé
with open("../.venv/.flask_secret_key", "wb") as key_file:
    key_file.write(encryption_key)

print("Clé de chiffrement générée et sauvegardée dans .flask_secret_key.")

# Charger la clé de chiffrement
with open("../.venv/.flask_secret_key", "rb") as key_file:
    encryption_key = key_file.read()

cipher = Fernet(encryption_key)

# Clé secrète Flask (modifie-la selon ton besoin)
flask_secret = b"ma_super_cle_secrete_123"

# Chiffrer la clé secrète Flask
encrypted_secret = cipher.encrypt(flask_secret)

# Sauvegarde dans un fichier sécurisé
with open("../.venv/flask_secret.enc", "wb") as secret_file:
    secret_file.write(encrypted_secret)

print("Clé secrète Flask chiffrée et sauvegardée dans flask_secret.enc.")