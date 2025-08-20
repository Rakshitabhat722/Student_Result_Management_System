from flask import Flask, render_template, request, redirect, url_for, session, flash
from db_config import get_db_connection

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong secret key

@app.route('/')
def home():
    return "🎓 Welcome to Student Result Management System!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']  # username from form
        password = request.form['password']  # password from form
        role = request.form['user_type']     # 'student' or 'admin'

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM users1 WHERE username = %s AND password = %s AND role = %s"
        cursor.execute(query, (username, password, role))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['user_type'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!')

    return render_template('login.html')
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_type = session.get('user_type')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if user_type == 'student':
        # Get student info
        query_student = """
            SELECT username, usn, branch, semester
            FROM users1
            WHERE user_id = %s
        """
        cursor.execute(query_student, (user_id,))
        student = cursor.fetchone()

        # Get marks
        query_marks = """
            SELECT subject, marks
            FROM marks1
            WHERE user_id = %s
        """
        cursor.execute(query_marks, (user_id,))
        marks = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('student_dashboard.html', student=student, marks=marks)

    elif user_type == 'admin':
        cursor.close()
        conn.close()
        return redirect(url_for('admin_dashboard'))

    else:
        cursor.close()
        conn.close()
        return redirect(url_for('login'))


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get all students and their marks
    cursor.execute("""
        SELECT u.user_id, u.username, u.usn, u.branch, u.semester, m.subject, m.marks
        FROM users1 u
        LEFT JOIN marks1 m ON u.user_id = m.user_id
        WHERE u.role = 'student'
    """)
    students = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin_dashboard.html', students=students)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'user_id' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usn = request.form['usn']
        branch = request.form['branch']
        semester = request.form['semester']

        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO users1 (username, password, role, usn, branch, semester)
            VALUES (%s, %s, 'student', %s, %s, %s)
        """
        cursor.execute(insert_query, (username, password, usn, branch, semester))
        conn.commit()
        cursor.close()
        conn.close()

        flash("New student added successfully!")
        return redirect(url_for('admin_dashboard'))

    return render_template('add_student.html')
@app.route('/edit_marks/<int:user_id>', methods=['GET', 'POST'])
def edit_marks(user_id):
    if 'user_id' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        subject = request.form['subject']
        marks = request.form['marks']

        # Check if marks for that subject already exist
        cursor.execute("SELECT * FROM marks1 WHERE user_id = %s AND subject = %s", (user_id, subject))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("UPDATE marks1 SET marks = %s WHERE user_id = %s AND subject = %s", (marks, user_id, subject))
        else:
            cursor.execute("INSERT INTO marks1 (user_id, subject, marks) VALUES (%s, %s, %s)", (user_id, subject, marks))

        conn.commit()
        flash("Marks updated successfully!")

    # Fetch student details
    cursor.execute("SELECT username, usn FROM users1 WHERE user_id = %s", (user_id,))
    student = cursor.fetchone()

    # Fetch all marks for display
    cursor.execute("SELECT subject, marks FROM marks1 WHERE user_id = %s", (user_id,))
    marks_list = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('edit_marks.html', student=student, marks_list=marks_list, user_id=user_id)
@app.route('/add_marks/<int:user_id>', methods=['GET', 'POST'])
def add_marks(user_id):
    if request.method == 'POST':
        subject = request.form['subject']
        marks = request.form['marks']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the user_id exists
        cursor.execute("SELECT * FROM users1 WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            cursor.close()
            conn.close()
            return "❌ User ID does not exist in users1 table", 400

        # Insert marks
        cursor.execute(
            "INSERT INTO marks1 (user_id, subject, marks) VALUES (%s, %s, %s)",
            (user_id, subject, marks)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('admin_dashboard'))

    return render_template('add_marks.html', user_id=user_id)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
