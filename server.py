from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Database setup
DATABASE = 'school_roll.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY name ASC")
    students = cursor.fetchall()
    conn.close()
    return render_template('index.html', students=students)

@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']
    if name:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/add_grade', methods=['POST'])
def add_grade():
    student_id = request.form['student_id']
    grade = request.form['grade']
    pdf_path = request.form['pdf_path']
    
    if student_id and grade and pdf_path:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO grades (student_id, grade, date, pdf_path) VALUES (?, ?, ?, ?)",
                       (student_id, grade, datetime.now().strftime("%Y-%m-%d"), pdf_path))
        conn.commit()
        conn.close()
    
    return redirect(url_for('index'))

@app.route('/view_grades/<int:student_id>')
def view_grades(student_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, grade, date, pdf_path FROM grades WHERE student_id = ?", (student_id,))
    grades = cursor.fetchall()
    conn.close()
    return jsonify(grades)

@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    cursor.execute("DELETE FROM grades WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1509, debug=True)