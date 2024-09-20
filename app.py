# Database structure
classroom_db = {
    "Classrooms": {f"Classroom {i + 1}": [] for i in range(10)},  # 10 classrooms
    "Students": [],
    "Teachers": [],
    "Schedules": {}
}
import random

# Time slots
time_slots = [f"{hour}:{minute:02d} {'AM' if hour < 12 else 'PM'}" for hour in range(8, 6) for minute in [0, 30]]

def add_student(name):
    classroom_db["Students"].append(name)

def add_teacher(name):
    classroom_db["Teachers"].append(name)

def add_classroom(name):
    if name not in classroom_db["Classrooms"]:
        classroom_db["Classrooms"][name] = []

def generate_schedule():
    schedule = {teacher: [] for teacher in classroom_db["Teachers"]}
    for slot in time_slots:
        for classroom in classroom_db["Classrooms"].keys():
            if classroom_db["Teachers"]:
                teacher = random.choice(classroom_db["Teachers"])
                schedule[teacher].append((slot, classroom))
    classroom_db["Schedules"] = schedule
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/role', methods=['POST'])
def role():
    user_role = request.form['role']
    return redirect(url_for(user_role.lower()))

@app.route('/admin')
def admin():
    return render_template('admin.html', classrooms=classroom_db["Classrooms"], students=classroom_db["Students"], teachers=classroom_db["Teachers"])

@app.route('/add_student', methods=['POST'])
def add_student_route():
    name = request.form['student_name']
    add_student(name)
    return redirect(url_for('admin'))

@app.route('/add_teacher', methods=['POST'])
def add_teacher_route():
    name = request.form['teacher_name']
    add_teacher(name)
    return redirect(url_for('admin'))

@app.route('/add_classroom', methods=['POST'])
def add_classroom_route():
    name = request.form['classroom_name']
    add_classroom(name)
    return redirect(url_for('admin'))

@app.route('/generate_schedule', methods=['POST'])
def generate_schedule_route():
    generate_schedule()
    return redirect(url_for('admin'))

@app.route('/teacher/<name>')
def teacher_schedule(name):
    schedule = classroom_db["Schedules"].get(name, [])
    return render_template('schedule.html', user=name, schedule=schedule)

@app.route('/student/<name>')
def student_schedule(name):
    # For simplicity, we'll assume a student can view the same schedule as their assigned teacher
    schedule = classroom_db["Schedules"].get(random.choice(classroom_db["Teachers"]), [])
    return render_template('schedule.html', user=name, schedule=schedule)

if __name__ == "__main__":
    app.run(debug=True)
