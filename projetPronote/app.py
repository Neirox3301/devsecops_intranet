from flask import Flask
from login_check import login_bp
from dashboard import dashboard_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Enregistrement des Blueprints
app.register_blueprint(login_bp)
app.register_blueprint(dashboard_bp)

if __name__ == '__main__':
    app.run(debug=True)
