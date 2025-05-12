from flask import Flask, request, render_template
import sqlite3
import hashlib

app = Flask(__name__)

def pripoj_db():
    conn = sqlite3.connect("kurzy.db")
    return conn

def query_db(query, args=(), commit=False):
    conn = pripoj_db()
    cursor = conn.cursor()
    cursor.execute(query, args)
    if commit:
        conn.commit()
        conn.close()
        return
    data = cursor.fetchall()
    conn.close()
    return data

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def affine_encrypt(text):
    A = 5
    B = 8
    encrypted_text = ""
    for char in text:
        if char.isalpha():
            char = char.upper()
            x = ord(char) - ord('A')
            encrypted_char = (A * x + B) % 26
            encrypted_text += chr(encrypted_char + ord('A'))
        else:
            encrypted_text += char
    return encrypted_text

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/kurzy')
def kurzy():
    query = "SELECT * FROM Kurzy_View"
    data = query_db(query)
    return render_template("kurzy.html", data=data)

@app.route('/treneri_kurzy')
def treneri_kurzy():
    query = "SELECT * FROM Treneri_Kurzy_View"
    data = query_db(query)
    return render_template("treneri.html", data=data)

@app.route('/treneri_priezvisko')
def treneri_priezvisko():
    query = "SELECT * FROM Treneri_Priezvisko_View"
    data = query_db(query)
    return render_template("treneri_priezvisko.html", data=data)

@app.route('/sucet_kapacita')
def sucet_kapacita():
    query = "SELECT SUM(Max_pocet_ucastnikov) FROM Kurzy WHERE Nazov_kurzu LIKE 'P%'"
    data = query_db(query)
    return render_template("sucet_kapacita.html", kapacita=data[0][0])

@app.route('/registracia', methods=['GET'])
def registracia_form():
    return render_template("registracia.html")

@app.route('/registracia', methods=['POST'])
def registracia_trenera():
    meno = request.form['meno']
    priezvisko = request.form['priezvisko']
    specializacia = request.form['specializacia']
    telefon = request.form['telefon']
    heslo = request.form['heslo']
    heslo_hash = hash_password(heslo)
    query = '''INSERT INTO Treneri (Meno, Priezvisko, Specializacia, Telefon, Heslo)
               VALUES (?, ?, ?, ?, ?)'''
    query_db(query, args=(meno, priezvisko, specializacia, telefon, heslo_hash), commit=True)
    return render_template("registracia_uspesna.html")

@app.route('/add_course_form', methods=['GET'])
def add_course_form():
    return render_template("pridat_kurz.html")

@app.route('/add_course', methods=['POST'])
def add_course():
    course_name = request.form['course_name']
    course_type = request.form['course_type']
    capacity = request.form['capacity']
    trainer_id = request.form['trainer_id']
    encrypted_name = affine_encrypt(course_name)
    encrypted_type = affine_encrypt(course_type)
    query = '''INSERT INTO Kurzy (nazov_kurzu, typ_sportu, max_pocet_ucastnikov, id_trenera)
               VALUES (?, ?, ?, ?)'''
    query_db(query, args=(encrypted_name, encrypted_type, capacity, trainer_id), commit=True)
    return render_template("kurz_uspesne_pridany.html")

if __name__ == '__main__':
    app.run(debug=True)
