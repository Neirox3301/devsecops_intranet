from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')

    print(f"Nom: {nom}, Prénom: {prenom}")

    return f"Bonjour {prenom} {nom}, vos données ont été reçues !"

if __name__ == '__main__':
    app.run(debug=True)
