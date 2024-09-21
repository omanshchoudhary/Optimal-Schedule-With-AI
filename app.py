from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
from datetime import datetime, timedelta
import json
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scheduler.db'
db = SQLAlchemy(app)

# Set up Gemini API
genai.configure(api_key='AIzaSyC0L-7I7IFbhazdjBqR66VFhvXWk9zwdzA')
model = genai.GenerativeModel('gemini-pro')

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class ClassID(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class_id.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    day = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            if (user_type == 'admin' and user.is_admin) or (user_type == 'student' and not user.is_admin):
                session['user_id'] = user.id
                session['is_admin'] = user.is_admin
                return redirect(url_for('dashboard'))
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return 'Username already exists'
        new_user = User(username=username, password=generate_password_hash(password), is_admin=(user_type == 'admin'))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', is_admin=session.get('is_admin', False))

@app.route('/add_data', methods=['POST'])
def add_data():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data_type = request.form['type']
    name = request.form['name']
    
    if data_type == 'class':
        new_item = ClassID(name=name)
    elif data_type == 'faculty':
        new_item = Faculty(name=name)
    elif data_type == 'venue':
        new_item = Venue(name=name)
    else:
        return jsonify({'error': 'Invalid data type'}), 400
    
    db.session.add(new_item)
    db.session.commit()

    # Generate new schedule after adding data
    generate_ai_schedule()

    return jsonify({'success': True})

def generate_ai_schedule():
    classes = ClassID.query.all()
    faculties = Faculty.query.all()
    venues = Venue.query.all()
    
    prompt = f"""
    Generate an optimized class schedule for the following:
    Classes: {[c.name for c in classes]}
    Faculties: {[f.name for f in faculties]}
    Venues: {[v.name for v in venues]}

    Constraints:
    1. 4 sessions of 50 minutes each per day for each class
    2. Classes should be between 8 AM and 2 PM
    3. Include a 10-minute break between sessions
    4. Schedule for Monday to Friday
    5. No time conflicts (no two classes should have the same faculty or venue at the same time)
    6. Optimize for time-saving and increased productivity

    Please provide the schedule in a structured format that can be easily parsed, such as:
    [
        {{"day": "Monday", "start_time": "08:00", "end_time": "08:50", "class": "Math", "faculty": "Dr. Smith", "venue": "Room 101"}},
        ...
    ]
    """
    
    response = model.generate_content(prompt)
    schedule_data = json.loads(response.text)
    
    # Clear existing schedule
    Schedule.query.delete()
    
    # Save new schedule to database
    for item in schedule_data:
        class_id = ClassID.query.filter_by(name=item['class']).first().id
        faculty_id = Faculty.query.filter_by(name=item['faculty']).first().id
        venue_id = Venue.query.filter_by(name=item['venue']).first().id
        new_schedule = Schedule(
            class_id=class_id,
            faculty_id=faculty_id,
            venue_id=venue_id,
            day=item['day'],
            start_time=item['start_time'],
            end_time=item['end_time']
        )
        db.session.add(new_schedule)
    
    db.session.commit()

@app.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    generate_ai_schedule()
    return jsonify({'success': True, 'message': 'Schedule generated successfully'})

@app.route('/get_timetable', methods=['POST'])
def get_timetable():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
    
    class_name = request.form['class_id']
    class_id = ClassID.query.filter_by(name=class_name).first()
    
    if not class_id:
        return jsonify({'error': 'Class not found'}), 404
    
    schedule = Schedule.query.filter_by(class_id=class_id.id).all()
    
    timetable = []
    for item in schedule:
        class_name = ClassID.query.get(item.class_id).name
        faculty_name = Faculty.query.get(item.faculty_id).name
        venue_name = Venue.query.get(item.venue_id).name
        timetable.append({
            'day': item.day,
            'start_time': item.start_time,
            'end_time': item.end_time,
            'class': class_name,
            'faculty': faculty_name,
            'venue': venue_name
        })
    
    return jsonify({'timetable': timetable})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
