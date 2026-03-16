from flask import Flask, request, redirect
import mysql.connector

app = Flask(__name__)

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="leave_system"
)

cursor = db.cursor()

@app.route('/register', methods=['POST'])
def register():

    id = request.form['id']
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    # Student ID validation
    if role == "Student":
        if not (id.startswith('N') or id.startswith('n')):
            return "Student ID must start with N or n"

    sql = "INSERT INTO users (id,name,email,password,role) VALUES (%s,%s,%s,%s,%s)"
    values = (id,name,email,password,role)

    cursor.execute(sql,values)
    db.commit()

    return "Registration Successful"

if __name__ == '__main__':
    app.run(debug=True)