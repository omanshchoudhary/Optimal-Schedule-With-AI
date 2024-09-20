import sqlite3

def init_db():
    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    # Create tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS classrooms (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS timetable (
            id INTEGER PRIMARY KEY,
            student_id INTEGER,
            classroom_id INTEGER,
            teacher_id INTEGER,
            slot TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id),
            FOREIGN KEY(classroom_id) REFERENCES classrooms(id),
            FOREIGN KEY(teacher_id) REFERENCES teachers(id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
