from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('university.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    search_type = request.args.get('type', 'name')
    conn = get_db_connection()

    if search_type == 'name':
        sql = """
        SELECT s.ID, s.name, s.dept_name, s.tot_cred
        FROM student s
        WHERE s.name LIKE ?
        """
    else:
        sql = """
        SELECT s.ID, s.name, s.dept_name, s.tot_cred
        FROM student s
        WHERE s.ID LIKE ?
        """

    students = conn.execute(sql, (f'%{query}%',)).fetchall()
    conn.close()
    return render_template('results.html', students=students)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    conn = get_db_connection()
    departments = conn.execute("SELECT dept_name FROM department").fetchall()

    if request.method == 'POST':
        ID = request.form['ID']
        name = request.form['name']
        dept_name = request.form['dept_name']
        is_transfer = request.form.get('transfer', 'no') == 'yes'
        tot_cred = request.form['tot_cred'] if is_transfer else 0

        conn.execute("""
            INSERT INTO student (ID, name, dept_name, tot_cred)
            VALUES (?, ?, ?, ?)
        """, (ID, name, dept_name, tot_cred))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('add_student.html', departments=departments)

@app.route('/schedule/<student_id>', methods=['GET'])
def schedule(student_id):
    year_filter = request.args.get('year')

    conn = get_db_connection()

    student_info = conn.execute("SELECT ID, name FROM student WHERE ID = ?", (student_id,)).fetchone()
    if not student_info:
        return "Student not found", 404

    year_query = "AND t.year = ?" if year_filter else ""
    args = (student_id,) if not year_filter else (student_id, year_filter)

    query = f"""
        SELECT t.course_id, t.semester, t.year
        FROM takes t
        WHERE t.ID = ?
        {year_query}
        ORDER BY t.year DESC, t.semester
    """
    schedule = conn.execute(query, args).fetchall()

    years = conn.execute("SELECT DISTINCT year FROM takes WHERE ID = ? ORDER BY year DESC", (student_id,)).fetchall()
    conn.close()
    return render_template('schedule.html', student=student_info, schedule=schedule, years=years, selected_year=year_filter)
