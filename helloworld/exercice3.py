from flask import Flask, request, render_template

class Student:
    def __init__(self, id, nom, prenom, notes_matiere1, notes_matiere2, notes_matiere3, notes_matiere4, notes_matiere5):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.notes_matiere1 = notes_matiere1
        self.notes_matiere2 = notes_matiere2
        self.notes_matiere3 = notes_matiere3
        self.notes_matiere4 = notes_matiere4
        self.notes_matiere5 = notes_matiere5
        
    def print_info(self):
        return (
            f"ID: {self.id}<br>"
            f"Nom: {self.nom}<br>"
            f"Prenom: {self.prenom}<br>"
            f"Notes Matiere 1: {self.notes_matiere1}<br>"
            f"Notes Matiere 2: {self.notes_matiere2}<br>"
            f"Notes Matiere 3: {self.notes_matiere3}<br>"
            f"Notes Matiere 4: {self.notes_matiere4}<br>"
            f"Notes Matiere 5: {self.notes_matiere5}"
        )  

    def get_info(self):
        return (
            f"ID: {self.id}"
            f"Nom: {self.nom}"
            f"Prenom: {self.prenom}"
            f"Notes Matiere 1: {self.notes_matiere1}"
            f"Notes Matiere 2: {self.notes_matiere2}"
            f"Notes Matiere 3: {self.notes_matiere3}"
            f"Notes Matiere 4: {self.notes_matiere4}"
            f"Notes Matiere 5: {self.notes_matiere5}"
        ) 

students = [
    Student(0, "Renaud", "Gérard", [12, 14, 16], [15, 13, 14], [10, 11, 12], [18, 17, 16], [14, 15, 16]),
    Student(1, "Martin", "Marie", [13, 15, 17], [16, 14, 15], [11, 12, 13], [19, 18, 17], [15, 16, 17]),
    Student(2, "Bernard", "Luc", [14, 16, 18], [17, 15, 16], [12, 13, 14], [20, 19, 18], [16, 17, 18]),
    Student(3, "Dubois", "Sophie", [15, 17, 19], [18, 16, 17], [13, 14, 15], [21, 20, 19], [17, 18, 19]),
    Student(4, "Durand", "Paul", [16, 18, 20], [19, 17, 18], [14, 15, 16], [22, 21, 20], [18, 19, 20])
]


app = Flask(__name__)

@app.route("/GET")
def get_students_list():
    """Get the info of all students"""
    data = f"<p>========== Students ==========<br>"
    for student in students:
        data += f"{student.print_info()}<br>" + "-"*230
        data += "</p>"
    return data

@app.route("/GET/<id>")
def get_student_info(id):
    """Get the info of one student"""
    for student in students:
        if student.id == int(id):
            return student.print_info()
    return f"<p> Sorry, couldn't find the student with ID : {id}"

@app.route("/POST", methods=["GET"])
def add_student():
    """Create a new student"""
    try:
        nom = request.args.get('nom')
        prenom = request.args.get('prenom')
        notes_matiere1 = list(map(int, request.args.get('notes_matiere1').split(',')))
        notes_matiere2 = list(map(int, request.args.get('notes_matiere2').split(',')))
        notes_matiere3 = list(map(int, request.args.get('notes_matiere3').split(',')))
        notes_matiere4 = list(map(int, request.args.get('notes_matiere4').split(',')))
        notes_matiere5 = list(map(int, request.args.get('notes_matiere5').split(',')))
        
        new_student = Student(len(students), nom, prenom, notes_matiere1, notes_matiere2, notes_matiere3, notes_matiere4, notes_matiere5)
        students.append(new_student)
        
        return f"<p>Student {nom} {prenom} added successfully!</p>"

    except:
        return f"<p>There was an error trying to create the student, please try again</p>"
    
@app.route("/PUT", methods=["GET"])
def modify_student():
    """Change a student grades"""
    try:
        id = int(request.args.get('id'))
        notes_matiere1 = list(map(int, request.args.get('notes_matiere1').split(',')))
        notes_matiere2 = list(map(int, request.args.get('notes_matiere2').split(',')))
        notes_matiere3 = list(map(int, request.args.get('notes_matiere3').split(',')))
        notes_matiere4 = list(map(int, request.args.get('notes_matiere4').split(',')))
        notes_matiere5 = list(map(int, request.args.get('notes_matiere5').split(',')))
        
        for student in students:
            if student.id == id:
                student.notes_matiere1 = notes_matiere1
                student.notes_matiere2 = notes_matiere2
                student.notes_matiere3 = notes_matiere3
                student.notes_matiere4 = notes_matiere4
                student.notes_matiere5 = notes_matiere5
                return f"<p>Student with ID {id} updated successfully!</p>"
            
        return f"<p>Sorry, counld't find the student with id : {id}, please try again...</p>"

    except:
        return f"<p>There was an error trying to create the student, please try again...</p>"
    

@app.route("/page")
def page():
    return render_template('index.html', students=students)
    