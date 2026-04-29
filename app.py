from flask import Flask, render_template, request, jsonify, session, Response
import sqlite3
import csv
import io

app = Flask(__name__)
app.secret_key = "devops_elite_2026"

def get_db():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn

with get_db() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, roll TEXT UNIQUE NOT NULL,
            course TEXT NOT NULL, attendance INTEGER DEFAULT 0
        )
    """)
    conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/students')
def get_students():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    return jsonify([dict(r) for r in rows])

# NEW: Dashboard Stats Route
@app.route('/stats')
def stats():
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        sum_att = conn.execute("SELECT SUM(attendance) FROM students").fetchone()[0] or 0
        top_course = conn.execute("SELECT course FROM students GROUP BY course ORDER BY COUNT(*) DESC LIMIT 1").fetchone()
        course_name = top_course[0] if top_course else "N/A"
    return jsonify({
        "total": total,
        "attendance": sum_att,
        "top_course": course_name
    })

@app.route('/add', methods=['POST'])
def add():
    data = request.json
    try:
        with get_db() as conn:
            conn.execute("INSERT INTO students (name, roll, course) VALUES (?, ?, ?)", 
                         (data['name'], data['roll'], data['course']))
            conn.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": "Duplicate Roll or Invalid Data"}), 400

@app.route('/mark_attendance/<int:id>', methods=['POST'])
def attend(id):
    with get_db() as conn:
        conn.execute("UPDATE students SET attendance = attendance + 1 WHERE id=? ", (id,))
        conn.commit()
    return jsonify({"status": "marked"})

@app.route('/update/<int:id>', methods=['PUT'])
def update(id):
    data = request.json
    with get_db() as conn:
        conn.execute("UPDATE students SET name=?, roll=?, course=? WHERE id=?", (data['name'], data['roll'], data['course'], id))
        conn.commit()
    return jsonify({"status": "updated"})

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    with get_db() as conn:
        conn.execute("DELETE FROM students WHERE id=?", (id,))
        conn.commit()
    return jsonify({"status": "deleted"})

@app.route('/analytics')
def analytics():
    with get_db() as conn:
        cursor = conn.execute("SELECT course, COUNT(*) as count FROM students GROUP BY course")
        course_data = {row['course']: row['count'] for row in cursor.fetchall()}
    return jsonify({"courses": course_data})

@app.route('/export')
def export():
    with get_db() as conn:
        cursor = conn.execute("SELECT name, roll, course, attendance FROM students")
        rows = cursor.fetchall()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Name', 'Roll', 'Course', 'Attendance'])
    for r in rows: cw.writerow([r[0], r[1], r[2], r[3]])
    return Response(si.getvalue(), mimetype="text/csv", headers={"Content-disposition": "attachment; filename=report.csv"})

if __name__ == '__main__':
    app.run(debug=True)