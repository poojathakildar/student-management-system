from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

# Initialize DB
def init_db():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            roll TEXT UNIQUE,
            course TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template("index.html")

# Add student
@app.route('/add', methods=['POST'])
def add_student():
    data = request.json
    try:
        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (name, roll, course) VALUES (?, ?, ?)",
            (data['name'], data['roll'], data['course'])
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Student added"})
    except:
        return jsonify({"message": "Roll number already exists"})

# Get students
@app.route('/students', methods=['GET'])
def get_students():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

# Delete
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"})

# Update
@app.route('/update/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.json
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE students SET name=?, roll=?, course=? WHERE id=?",
        (data['name'], data['roll'], data['course'], id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Updated"})

if __name__ == '__main__':
    app.run(debug=True)