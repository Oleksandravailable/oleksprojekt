from flask import Flask, request, jsonify
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
    return '''
        <h1>Výber z databázy</h1>
        <a href="/registracia"><button>Registruj trénera</button></a>
        <a href="/treneri_kurzy"><button>Tréneri a ich kurzy</button></a>
        <a href="/kurzy"><button>Kurzy</button></a>
        <a href="/treneri_priezvisko"><button>Tréneri podľa priezviska</button></a>
        <a href="/sucet_kapacita"><button>Súčet kapacity kurzov (P)</button></a>
        <a href="/add_course_form"><button>Pridať kurz</button></a>
        <hr>
    '''

@app.route('/treneri_kurzy')
def treneri_kurzy():
    query = "SELECT * FROM Treneri_Kurzy_View"
    data = query_db(query)
    vystup = "<h2>Zoznam trénerov a ich kurzov:</h2>"
    for trener in data:
        vystup += f"<p>{trener}</p>"
    vystup += '<a href="/"><button>Späť</button></a>'
    return vystup

@app.route('/kurzy')
def kurzy():
    query = "SELECT * FROM Kurzy_View"
    data = query_db(query)
    vystup = "<h2>Zoznam kurzov:</h2>"
    for kurz in data:
        vystup += f"<p>{kurz}</p>"
    vystup += '<a href="/"><button>Späť</button></a>'
    return vystup

@app.route('/treneri_priezvisko')
def treneri_priezvisko():
    query = "SELECT * FROM Treneri_Priezvisko_View"
    data = query_db(query)
    vystup = "<h2>Tréneri podľa priezviska:</h2>"
    for trener in data:
        vystup += f"<p>{trener}</p>"
    vystup += '<a href="/"><button>Späť</button></a>'
    return vystup

@app.route('/sucet_kapacita')
def sucet_kapacita():
    query = "SELECT SUM(Max_pocet_ucastnikov) FROM Kurzy WHERE Nazov_kurzu LIKE 'P%'"
    data = query_db(query)
    vystup = f"<h2>Súčet maximálnej kapacity kurzov, ktoré začínajú na 'P': {data[0][0]}</h2>"
    vystup += '<a href="/"><button>Späť</button></a>'
    return vystup

@app.route('/registracia', methods=['GET'])
def registracia_form():
    return '''
        <h2>Registrácia trénera</h2>
        <form action="/registracia" method="post">
            <label>Meno:</label><br>
            <input type="text" name="meno" required><br><br>
            <label>Priezvisko:</label><br>
            <input type="text" name="priezvisko" required><br><br>
            <label>Špecializácia:</label><br>
            <input type="text" name="specializacia" required><br><br>
            <label>Telefón:</label><br>
            <input type="text" name="telefon" required><br><br>
            <label>Heslo:</label><br>
            <input type="password" name="heslo" required><br><br>
            <button type="submit">Registrovať</button>
        </form>
        <hr>
        <a href="/"><button>Späť</button></a>
    '''

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
    return '''
        <h2>Tréner bol úspešne zaregistrovaný!</h2>
        <hr>
        <a href="/"><button>Späť</button></a>
    '''

@app.route('/add_course_form', methods=['GET'])
def add_course_form():
    return '''
        <h2>Pridať kurz</h2>
        <form action="/add_course" method="post">
            <label>Názov kurzu:</label><br>
            <input type="text" name="course_name" required><br><br>
            <label>Typ športu:</label><br>
            <input type="text" name="course_type" required><br><br>
            <label>Maximálna kapacita:</label><br>
            <input type="number" name="capacity" required><br><br>
            <label>ID trénera:</label><br>
            <input type="number" name="trainer_id" required><br><br>
            <button type="submit">Pridať kurz</button>
        </form>
        <hr>
        <a href="/"><button>Späť</button></a>
    '''

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
    return '''
        <h2>Kurz bol úspešne pridaný!</h2>
        <hr>
        <a href="/"><button>Späť</button></a>
    '''

if __name__ == '__main__':
    app.run(debug=True)
