from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
import plotly.express as px
import plotly.io as pio
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database helper functions
def query_db(query, args=(), one=False):
    conn = sqlite3.connect('school_roll.db')
    conn.row_factory = sqlite3.Row
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    conn = sqlite3.connect('school_roll.db')
    conn.execute(query, args)
    conn.commit()
    conn.close()

# Routes
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'admin' and password == '0':
            session['user_name'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        
        student = query_db('SELECT id, name FROM students WHERE name = ?', [username], one=True)
        if student and str(student['id']) == password:
            session['user_name'] = student['name']
            session['user_id'] = student['id']
            return redirect(url_for('student_dashboard'))
        
        flash('Invalid credentials. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/admin', methods=['GET'])
def admin_dashboard():
    if 'user_name' not in session or session['user_name'] != 'admin':
        return redirect(url_for('login'))
    students = query_db('SELECT id, name FROM students')
    return render_template('admin_dashboard.html', students=students)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'user_name' not in session or session['user_name'] != 'admin':
        # Corrected 'index' to 'login'
        return redirect(url_for('login'))  
    
    if request.method == 'POST':
        student_name = request.form['name']
        if student_name:
            execute_db('INSERT INTO students (name) VALUES (?)', [student_name])
            flash('Student added successfully.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Student name cannot be empty.', 'error')
    
    return render_template('add_student.html')

@app.route('/add_grade/<int:student_id>', methods=['GET', 'POST'])
def add_grade(student_id):
    if 'user_name' not in session or session['user_name'] != 'admin':
        return redirect(url_for('login'))
    
    student = query_db('SELECT name FROM students WHERE id = ?', [student_id], one=True)
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        grade = request.form['grade']
        date = request.form['date']
        file_link = request.form['file_link']
        
        if grade and date and file_link:
            execute_db('INSERT INTO grades (student_id, grade, date, pdf_path) VALUES (?, ?, ?, ?)',
                       [student_id, grade, date, file_link])
            flash('Grade added successfully.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('All fields are required.', 'error')
    
    return render_template('add_grade.html', student_name=student['name'], student_id=student_id)

@app.route('/admin/view-grades/<int:student_id>', methods=['GET'])
def view_grades(student_id):
    student = query_db('SELECT * FROM students WHERE id = ?', [student_id], one=True)
    if not student:
        return "Student not found", 404
    
    # Fetch grades and dates
    grades = query_db('SELECT grade, date, pdf_path AS file_link FROM grades WHERE student_id = ?', [student_id])
    
    # Prepare data for the bar chart (grades over time)
    grade_data = query_db('SELECT grade, date FROM grades WHERE student_id = ?', [student_id])
    grades_list = []
    dates_list = []
    
    for grade in grade_data:
        grades_list.append(grade['grade'])
        dates_list.append(grade['date'])
    
    # Generate the plot (bar chart)
    if grades_list:
        fig = px.bar(x=dates_list, y=grades_list, labels={'x': 'Date', 'y': 'Grade'}, title="Grades Over Time")
        fig.update_layout(showlegend=False)

        # Convert plot to HTML div
        graph_html = pio.to_html(fig, full_html=False)
    else:
        graph_html = None

    return render_template('view_grades.html', student=student, grades=grades, graph_html=graph_html)

@app.route('/student_dashboard', methods=['GET'])
def student_dashboard():
    if 'user_name' not in session or 'user_id' not in session:
        return redirect(url_for('login'))
    
    student_id = session['user_id']
    grades = query_db('SELECT grade, date, pdf_path AS file_link FROM grades WHERE student_id = ?', [student_id])
    
    # Prepare data for the bar chart (grades over time)
    grade_data = query_db('SELECT grade, date FROM grades WHERE student_id = ?', [student_id])
    grades_list = []
    dates_list = []
    
    for grade in grade_data:
        grades_list.append(grade['grade'])
        dates_list.append(grade['date'])
    
    # Generate the plot (bar chart)
    if grades_list:
        fig = px.bar(x=dates_list, y=grades_list, labels={'x': 'Date', 'y': 'Grade'}, title="Your Grades Over Time")
        fig.update_layout(showlegend=False)

        # Convert plot to HTML div
        graph_html = pio.to_html(fig, full_html=False)
    else:
        graph_html = None

    return render_template('student_dashboard.html', grades=grades, graph_html=graph_html, user_name=session['user_name'])

@app.route('/grades_test', methods=['GET', 'POST'])
def grades_test():
    if 'user_name' not in session or session['user_name'] != 'admin':
        return redirect(url_for('login'))
    
    result = None  # Initialize result for rendering in template
    error = None   # Initialize error for handling invalid cases

    if request.method == 'POST':
        pdf_link = request.form['pdf_link']
        action = request.form['action']

        if not pdf_link:
            error = "You must enter a PDF link."
        elif action == "median":
            # Fetch grades for the specific PDF link
            grades = query_db('SELECT grade FROM grades WHERE pdf_path = ?', [pdf_link])
            if grades:
                grade_values = [float(row['grade']) for row in grades]
                median = sum(grade_values) / len(grade_values)  # Arithmetic median
                result = f"The median grade for the test is: {median:.2f}"
            else:
                error = "No grades found for the provided PDF link."
        elif action == "student":
            student_name = request.form.get('student_name')
            if not student_name:
                error = "You must enter a student's name to view their grade."
            else:
                # Fetch student grade for the specific PDF link
                grade = query_db(
                    '''SELECT grades.grade 
                       FROM grades 
                       JOIN students ON grades.student_id = students.id 
                       WHERE grades.pdf_path = ? AND students.name = ?''', 
                    [pdf_link, student_name], 
                    one=True
                )
                if grade:
                    result = f"The grade for {student_name} on this test is: {grade['grade']}"
                else:
                    error = f"No grade found for {student_name} on the provided test."
    
    return render_template('grades_test.html', result=result, error=error)

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Main entry point
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 1509, debug=True)
