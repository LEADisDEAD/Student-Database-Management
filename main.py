from flask import Flask, render_template, request,redirect,url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os

IS_RENDER = os.environ.get('RENDER', False)
# database configuration:
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # or your MySQL username
app.config['MYSQL_PASSWORD'] = '!@#123QWEqwe'  # your MySQL password
app.config['MYSQL_DB'] = 'students_flaskproj'

mysql = MySQL(app)


@app.route('/')
def home():
    return render_template("home.html",message=None)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/help.html')
def help_function():
    return render_template('about.html')

@app.route('/add',methods=["POST"])
def add_student():
    name = request.form["name"]
    age = request.form["age"]
    student_class = request.form["student_class"]

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO student_basic_info (name, age,student_class) VALUES (%s, %s,%s)", (name, age,student_class))
    mysql.connection.commit()
    cursor.close()

    message_student_added = f"✅ Student added: {name} ({age}) Class {student_class}"
    return render_template("home.html", add_message=message_student_added)

@app.route('/students')
def view_students():
    students = get_all_students()
    total_students = len(students)
    return render_template('students.html', students=students,total_students=total_students)


@app.route('/delete/<int:student_id>',methods=['POST'])
def delete_student(student_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE from student_basic_info where id=%s",(student_id,))
    mysql.connection.commit();
    cursor.close()

    return redirect('/students')

def get_all_students():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM student_basic_info")
    rows = cursor.fetchall()
    students = [dict(row) for row in rows]
    cursor.close()
    return students

@app.route('/edit/<int:student_id>')
def edit_student(student_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM student_basic_info WHERE id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    return render_template('edit.html', student=student)


@app.route('/update/<int:student_id>',methods=['POST'])
def update_student(student_id):
    name = request.form['name']
    age = request.form['age']
    student_class = request.form['student_class']

    cursor=mysql.connection.cursor()
    cursor.execute("UPDATE student_basic_info SET name=%s, age = %s,student_class=%s WHERE id=%s",(name,age,student_class,student_id))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('view_students'))

@app.route('/marks/<int:student_id>')
def view_marks(student_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM student_basic_info where id = %s",(student_id,))
    student = cursor.fetchone()

    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()

    cursor.execute("""
            SELECT sm.id, sm.marks, s.subject_name
            FROM student_marks sm
            JOIN subjects s ON sm.subject_id = s.id
            WHERE sm.student_id = %s
        """, (student_id,))
    marks = cursor.fetchall()
    # Prepare data for Chart.js
    subject_names = [mark['subject_name'] for mark in marks]
    subject_marks = [mark['marks'] for mark in marks]

    cursor.close()
    return render_template("marks.html", student=student, subjects=subjects, marks=marks,subject_names=subject_names, subject_marks=subject_marks)

@app.route('/marks/add/<int:student_id>',methods=['POST'])
def add_mark(student_id):
    subject_id = request.form['subject_id']
    marks = int(request.form['marks'])

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO student_marks (student_id, subject_id, marks) VALUES (%s, %s, %s)",
                   (student_id, subject_id, marks))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('view_marks', student_id=student_id))

@app.route('/marks/update/<int:mark_id>', methods=['POST'])
def update_mark(mark_id):
    new_marks = request.form['marks']

    cursor = mysql.connection.cursor()
    #student_id to redirect properly after update
    cursor.execute("SELECT student_id FROM student_marks WHERE id = %s", (mark_id,))
    student_id = cursor.fetchone()[0]

    cursor.execute("UPDATE student_marks SET marks = %s WHERE id = %s", (new_marks, mark_id))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('view_marks', student_id=student_id))


@app.route('/marks/delete/<int:mark_id>/<int:student_id>', methods=['POST'])
def delete_mark(mark_id, student_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM student_marks WHERE id = %s", (mark_id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('view_marks', student_id=student_id))



if __name__ == '__main__':
    if not IS_RENDER:
        app.run(debug=True)