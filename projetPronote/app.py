from flask import Flask
from model.login_check import login_bp
from model.dashboard import dashboard_bp
from model.dashboard_prof import dashboard_prof_bp  # Import du dashboard prof

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Enregistrement des Blueprints
app.register_blueprint(login_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(dashboard_prof_bp)  # Nouveau blueprint pour les professeurs

if __name__ == '__main__':
    app.run(debug=True)
