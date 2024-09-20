from flask import Flask, render_template, request, redirect
import sqlite3
import random

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('school.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']  # 'student', 'teacher', or 'classroom'
        
        conn = get_db_connection()
        try:
            if role == 'student':
                existing_student = conn.execute('SELECT id FROM students WHERE name = ?', (name,)).fetchone()
                if existing_student:
                    return "Student already exists!", 400
                conn.execute('INSERT INTO students (name) VALUES (?)', (name,))
                
            elif role == 'teacher':
                existing_teacher = conn.execute('SELECT id FROM teachers WHERE name = ?', (name,)).fetchone()
                if existing_teacher:
                    return "Teacher already exists!", 400
                conn.execute('INSERT INTO teachers (name) VALUES (?)', (name,))
                
            elif role == 'classroom':
                existing_classroom = conn.execute('SELECT id FROM classrooms WHERE name = ?', (name,)).fetchone()
                if existing_classroom:
                    return "Classroom already exists!", 400
                conn.execute('INSERT INTO classrooms (name) VALUES (?)', (name,))
                
            conn.commit()
        except sqlite3.IntegrityError as e:
            return f"An error occurred: {e}", 500
        finally:
            conn.close()
        return redirect('/admin')

    return render_template('admin.html')

@app.route('/timetable', methods=['GET', 'POST'])
def timetable():
    if request.method == 'POST':
        student_name = request.form['student_name']
        conn = get_db_connection()
        student = conn.execute('SELECT id FROM students WHERE name = ?', (student_name,)).fetchone()
        
        if student:
            # Generate and return the timetable for the student
            student_id = student['id']
            timetable_data = generate_timetable(student_id)
            return render_template('timetable.html', timetable=timetable_data)
        
    return render_template('timetable.html', timetable=None)

def generate_timetable(student_id):
    timetable = []
    conn = get_db_connection()
    
    # Fetch all available classrooms and teachers
    classrooms = conn.execute('SELECT id, name FROM classrooms').fetchall()
    teachers = conn.execute('SELECT id, name FROM teachers').fetchall()
    
    # Example time slots
    slots = ['8:30 AM - 9:30 AM', '9:30 AM - 10:30 AM', '10:30 AM - 11:30 AM', 
             '11:30 AM - 12:30 PM', '1:30 PM - 2:30 PM', '2:30 PM - 3:30 PM', 
             '3:30 PM - 4:30 PM', '4:30 PM - 5:30 PM']
    
    # Schedule students with breaks
    for i, slot in enumerate(slots):
        if random.random() < 0.5:  # 50% chance to skip a slot for a break
            timetable.append({
                'slot': slot,
                'classroom': 'Break',
                'teacher': ''
            })
        else:
            classroom = random.choice(classrooms)
            teacher = random.choice(teachers)
            timetable.append({
                'slot': slot,
                'classroom': classroom['name'],
                'teacher': teacher['name']
            })

    conn.close()
    return timetable

if __name__ == '__main__':
    app.run(debug=True)
