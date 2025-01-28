import requests, os
from flask import Flask
from dotenv import load_dotenv

app = Flask(__name__) 
load_dotenv()
API_KEY: str = os.getenv("API_KEY")

@app.route("/weather/<city>")
def get_weather(city): 
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=fr'
    r = requests.get(url)
    if r.status_code == 200:
        weather_data = r.json()
        return f"<p>===== Météo à {city.capitalize()} =====<br>Température actuelle : {weather_data['main']['temp']}°C<br>Temps : {weather_data['weather'][0]['description'].capitalize()}<br>Humidité : {weather_data['main']['humidity']}%<br>Vitesse du vent : {weather_data['wind']['speed']} km/h</p>"
    return f"<p>Erreur {r.status_code}: Impossible de récupérer les données météo.</p>"