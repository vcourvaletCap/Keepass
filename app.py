import json
from flask import Flask, render_template, request, redirect, url_for

from strongbox import Strongbox

app = Flask(__name__)

strongbox = None

    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nomcoffre = request.form['text']
        password = request.form['password']
        loaded_strongbox = Strongbox.load_strongbox("strongbox_data.json")
        for data in loaded_strongbox:
            loaded_box = Strongbox(data["identifier"])
            decrypted_password = loaded_box.fernet.decrypt(data["sb_password"].encode()).decode()
            print(decrypted_password)
            if decrypted_password == password and nomcoffre == data["identifier"]:
                return redirect(url_for('gestion',nomcoffre=nomcoffre))
            else:
                return "Mot de passe incorrect. Veuillez réessayer."
    else:
        return render_template('login.html')

@app.route('/creation', methods=['GET', 'POST'])
def creation():
    global strongbox
    if request.method == 'POST':
        nomcoffre = request.form['text']
        password = request.form['password']
        strongbox = Strongbox(identifier=nomcoffre)
        strongbox.initiate_password(password)
        strongbox.save_strongbox("strongbox_data.json")
        return redirect(url_for('gestion', nomcoffre=nomcoffre))
    else:
        return render_template('creation.html')

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/gestion', methods=['GET', 'POST'])
def gestion():
    if request.method == 'POST':
        nomcoffre = request.form['nomcoffre']
        site = request.form['site']
        password = request.form['password']

        with open("strongbox_data.json", "r+") as file:
            data = json.load(file)
            for data2 in data:
                if data2["identifier"] == nomcoffre:
                    loaded_box = Strongbox(data2["identifier"])
                    loaded_box.add_password(site, password)
                    data2['passwords'][site] = loaded_box.fernet.encrypt(password.encode()).decode()
                    file.seek(0)
                    json.dump(data,file)
                    file.truncate()
                    break
    with open("strongbox_data.json", "r") as file:
        data = json.load(file)
        for strongbox_data in data:
            if strongbox_data["identifier"] == request.args.get('nomcoffre'):
                passwords = strongbox_data.get("passwords", {})
                break
        else:
            passwords = {}

    nomcoffre = request.args.get('nomcoffre')
    return render_template('gestion.html', nomcoffre=nomcoffre,passwords=passwords)

@app.route('/modifier_mot_de_passe', methods=['GET','POST'])
def modifier_mot_de_passe():
    if request.method == 'POST':
        nomcoffre = request.form['nomcoffre']
        site = request.form['site']
        password = request.form['password2']

        loaded_box = Strongbox.load_strongbox("strongbox_data.json")
        for data in loaded_box:
            if data["identifier"] == nomcoffre:
                loaded_box = Strongbox(data["identifier"])
                loaded_box.update_password_from_strongbox("strongbox_data.json", nomcoffre, site, password)
                break
    return redirect(url_for('gestion', nomcoffre=nomcoffre))

@app.route('/modifier_mot_de_passe_html', methods=['GET','POST'])
def modifier_mot_de_passe2():
    if request.method == 'POST':
        nomcoffre = request.form['nomcoffre']
        site = request.form['site']
        return render_template('modification_password.html', nomcoffre=nomcoffre,site=site )
    else:
        return render_template('modification_password.html', nomcoffre=nomcoffre,site=site )

@app.route('/supprimer_mot_de_passe', methods=['POST'])
def supprimer_mot_de_passe():
    if request.method == 'POST':
        nomcoffre = request.form['nomcoffre']
        site = request.form['site']
        
        loaded_box = Strongbox.load_strongbox("strongbox_data.json")
        for data in loaded_box:
            if data["identifier"] == nomcoffre:
                loaded_box = Strongbox(data["identifier"])
                loaded_box.delete_password_from_strongbox("strongbox_data.json", nomcoffre, site)
                break

    return redirect(url_for('gestion', nomcoffre=nomcoffre))

@app.route('/export', methods=['POST'])
def export():
    if request.method == 'POST':
        nomcoffre = request.form['nomcoffre']
        Strongbox.export_strongbox(initial_filename="strongbox_data.json",export_filename="test.json", export_identifier=nomcoffre)
    return redirect(url_for('index'))

@app.route('/import', methods=['POST'])
def importe():
    if request.method == 'POST':
        f = request.files['file'] 
        f.save(f.filename)
        Strongbox.import_strongbox("strongbox_data.json",f.filename)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)