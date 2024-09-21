from flask import Flask, request, jsonify
import gemini
from database import conn, c  # Import the connection and cursor objects from database.py

app = Flask(__name__)

# Create a Gemini database object
db = gemini.Database(conn)

# Define a function to create a new student
def create_student(name, grade):
    # Use Gemini to create a new student
    student = db.table('students').insert({'name': name, 'grade': grade})
    return student

# Define a function to get all students
def get_students():
    # Use Gemini to retrieve all students
    students = db.table('students').all()
    return students

# Define a function to update a student's grade
def update_student_grade(student_id, new_grade):
    # Use Gemini to update the student's grade
    db.table('students').update({'grade': new_grade}, {'id': student_id})

# Define a function to delete a student
def delete_student(student_id):
    # Use Gemini to delete the student
    db.table('students').delete({'id': student_id})

# Define Flask routes for CRUD operations
@app.route('/students', methods=['POST'])
def create_student_route():
    name = request.json['name']
    grade = request.json['grade']
    student = create_student(name, grade)
    return jsonify({'id': student.id, 'name': student.name, 'grade': student.grade})

@app.route('/students', methods=['GET'])
def get_students_route():
    students = get_students()
    return jsonify([{'id': student.id, 'name': student.name, 'grade': student.grade} for student in students])

@app.route('/students/<int:student_id>', methods=['PATCH'])
def update_student_grade_route(student_id):
    new_grade = request.json['grade']
    update_student_grade(student_id, new_grade)
    return jsonify({'message': 'Student grade updated successfully'})

@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student_route(student_id):
    delete_student(student_id)
    return jsonify({'message': 'Student deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)
