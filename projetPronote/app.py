from flask import Flask
from model.login_check import login_bp
from model.dashboard import dashboard_bp
from model.dashboard_prof import dashboard_prof_bp

app = Flask(__name__)
app.secret_key = 'a'

app.register_blueprint(login_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(dashboard_prof_bp)

if __name__ == '__main__':
    app.run(debug=True)
