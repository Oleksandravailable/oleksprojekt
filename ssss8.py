from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import hashlib
import os

app = Flask(__name__, instance_relative_config=True)
db_path = os.path.join(app.instance_path, "kurzy.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}".replace("\\", "//")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Trener(db.Model):
    __tablename__ = "Treneri"
    ID_Trenera = db.Column(db.Integer, primary_key=True)
    Meno = db.Column(db.String, nullable=False)
    Priezvisko = db.Column(db.String, nullable=False)
    Specializacia = db.Column(db.String)
    Telefon = db.Column(db.String)
    Heslo = db.Column(db.String, nullable=False)
    Kurzy = db.relationship("Kurz", backref="Trener", lazy=True)

class Kurz(db.Model):
    __tablename__ = "Kurzy"
    ID_Kurzu = db.Column(db.Integer, primary_key=True)
    Nazov_Kurzu = db.Column(db.String, nullable=False)
    Typ_Sportu = db.Column(db.String)
    Max_Pocet_Ucastnikov = db.Column(db.Integer)
    ID_Trenera = db.Column(db.Integer, db.ForeignKey('Treneri.ID_Trenera'))  

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/kurzy')
def kurzy():
    kurzy = Kurz.query.all()
    return render_template("kurzy.html", kurzy=kurzy)

@app.route('/sucet_kapacita')
def sucet_kapacita():
    kapacita = db.session.query(db.func.sum(Kurz.Max_Pocet_Ucastnikov)).scalar()
    return render_template("sucet_kapacita.html", kapacita=kapacita)

@app.route('/treneri_priezvisko')
def treneri_priezvisko():
    treneri = Trener.query.order_by(Trener.Priezvisko).all()
    return render_template("treneri_priezvisko.html", treneri=treneri)

@app.route('/registracia', methods=['GET', 'POST'])
def registracia():
    if request.method == 'POST':
        meno = request.form['meno']
        priezvisko = request.form['priezvisko']
        specializacia = request.form['specializacia']
        telefon = request.form['telefon']
        heslo = request.form['heslo']
        heslo_hash = hashlib.sha256(heslo.encode()).hexdigest()

        novy_trener = Trener(Meno=meno, Priezvisko=priezvisko, Specializacia=specializacia, Telefon=telefon, Heslo=heslo_hash)
        db.session.add(novy_trener)
        db.session.commit()

        return render_template("registracia_uspesna.html")
    
    return render_template("registracia.html")

@app.route('/add_course_form')
def add_course_form():
    treneri = Trener.query.all()
    return render_template("pridat_kurz.html", treneri=treneri)

@app.route('/add_course', methods=['POST'])
def add_course():
    course_name = request.form['course_name']
    course_type = request.form['course_type']
    capacity = request.form['capacity']
    trainer_id = request.form['trainer_id']

    novy_kurz = Kurz(Nazov_Kurzu=course_name, Typ_Sportu=course_type, Max_Pocet_Ucastnikov=capacity, ID_Trenera=trainer_id)
    db.session.add(novy_kurz)
    db.session.commit()

    return render_template("kurz_uspesne_pridany.html")

@app.route('/treneri')
def treneri():
    treneri = Trener.query.all()
    return render_template("treneri.html", treneri=treneri)

@app.route('/Treneri_Kurzy')
def Treneri_Kurzy():
    treneri = Trener.query.all()
    return render_template("Treneri_Kurzy.html", treneri=treneri)

if __name__ == '__main__':
    app.run(debug=True)
