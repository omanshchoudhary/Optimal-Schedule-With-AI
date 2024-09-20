from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random

app = Flask(__name__)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('school.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Admin page for adding students, teachers, and classrooms
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form['action'] == 'Add Student':
            name = request.form['name']
            conn = get_db_connection()
            conn.execute('INSERT INTO students (name) VALUES (?)', (name,))
            conn.commit()
            conn.close()
        elif request.form['action'] == 'Add Teacher':
            name = request.form['name']
            conn = get_db_connection()
            conn.execute('INSERT INTO teachers (name) VALUES (?)', (name,))
            conn.commit()
            conn.close()
        elif request.form['action'] == 'Add Classroom':
            name = request.form['name']
            conn = get_db_connection()
            conn.execute('INSERT INTO classrooms (name) VALUES (?)', (name,))
            conn.commit()
            conn.close()
        return redirect(url_for('admin'))

    return render_template('admin.html')

# Generate timetable
@app.route('/timetable', methods=['GET', 'POST'])
def timetable():
    if request.method == 'POST':
        student_name = request.form['student_name']
        conn = get_db_connection()
        student = conn.execute('SELECT id FROM students WHERE name = ?', (student_name,)).fetchone()
        
        if student:
            student_id = student['id']
            # Placeholder timetable generation logic
            # You should implement a more balanced distribution logic here
            time_slots = [f"{hour}:00" for hour in range(8, 17)]  # 8 AM to 5 PM
            classrooms = conn.execute('SELECT * FROM classrooms').fetchall()
            teachers = conn.execute('SELECT * FROM teachers').fetchall()
            
            timetable_entries = []
            for slot in time_slots:
                classroom = random.choice(classrooms)
                teacher = random.choice(teachers)
                timetable_entries.append({
                    'timeslot': slot,
                    'classroom': classroom['name'],
                    'teacher': teacher['name']
                })
                
            return render_template('timetable.html', timetable=timetable_entries)

    return render_template('timetable.html', timetable=[])

if __name__ == '__main__':
    app.run(debug=True)
