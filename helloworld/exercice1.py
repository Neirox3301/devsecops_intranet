import requests
import csv
from flask import Flask 

URL: str = 'https://jsonplaceholder.typicode.com/todos'

app = Flask(__name__) 

@app.route("/") 
def print_todo_list(): 
    r = requests.get(URL)

    if r.status_code == 200:
        data = r.json()

        with open('todo_list.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            for elem in data:
                writer.writerow(elem.values())
        return data
