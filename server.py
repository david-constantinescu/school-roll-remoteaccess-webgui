from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key

def get_db():
    conn = sqlite3.connect('school_roll.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check for admin credentials
        if username == "admin" and password == "0":
            session['user_id'] = 0
            session['user_name'] = 'admin'
            session['is_admin'] = True
            db = get_db()
            students = db.execute('SELECT * FROM students').fetchall()
            return render_template('index.html', students=[dict(row) for row in students])
            
        db = get_db()
        user = db.execute(
            'SELECT * FROM students WHERE name = ? AND id = ?',
            (username, password)
        ).fetchone()
        
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if session.get('is_admin', False):
        db = get_db()
        students = db.execute('SELECT * FROM students').fetchall()
        return render_template('index.html', students=[dict(row) for row in students])
        
    db = get_db()
    user_id = session['user_id']
    
    grades = db.execute(
        'SELECT * FROM grades WHERE student_id = ?',
        (user_id,)
    ).fetchall()
    
    return render_template('dashboard.html', grades=[dict(row) for row in grades])

@app.route('/view_grades/<int:student_id>')
@login_required
def view_grades(student_id):
    if not session.get('is_admin', False):
        return redirect(url_for('dashboard'))
    
    db = get_db()
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    grades = db.execute(
        'SELECT * FROM grades WHERE student_id = ? ORDER BY date DESC',
        (student_id,)
    ).fetchall()
    
    return render_template('grades.html', student=dict(student), grades=[dict(row) for row in grades])

@app.route('/add_student', methods=['POST'])
@login_required
def add_student():
    if not session.get('is_admin', False):
        return redirect(url_for('dashboard'))
    
    name = request.form['name']
    db = get_db()
    db.execute('INSERT INTO students (name) VALUES (?)', (name,))
    db.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete_student/<int:student_id>')
@login_required
def delete_student(student_id):
    if not session.get('is_admin', False):
        return redirect(url_for('dashboard'))
    
    db = get_db()
    db.execute('DELETE FROM grades WHERE student_id = ?', (student_id,))
    db.execute('DELETE FROM students WHERE id = ?', (student_id,))
    db.commit()
    return redirect(url_for('dashboard'))

@app.route('/add_grade', methods=['GET', 'POST'])
@login_required
def add_grade():
    if not session.get('is_admin', False):
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        student_id = request.form['student_id']
        grade = request.form['grade']
        pdf_path = request.form['pdf_path']
        
        db = get_db()
        db.execute(
            'INSERT INTO grades (student_id, grade, date, pdf_path) VALUES (?, ?, date("now"), ?)',
            (student_id, grade, pdf_path)
        )
        db.commit()
        return redirect(url_for('view_grades', student_id=student_id))
    
    # GET request - show the add grade form
    db = get_db()
    students = db.execute('SELECT * FROM students').fetchall()
    return render_template('add_grade.html', students=[dict(row) for row in students])

@app.route('/get_student_grades/<int:student_id>')
@login_required
def get_student_grades(student_id):
    if not session.get('is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 403
    
    db = get_db()
    grades = db.execute(
        'SELECT grade, date, pdf_path FROM grades WHERE student_id = ? ORDER BY date DESC',
        (student_id,)
    ).fetchall()
    
    return jsonify([dict(grade) for grade in grades])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1509, debug=True)