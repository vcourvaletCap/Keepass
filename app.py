from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/creation')
def creation():
    return render_template('creation.html')

@app.route('/gestion')
def gestion():
    return render_template('gestion.html')

@app.route('/export')
def export():
    return render_template('exportation.html')

if __name__ == '__main__':
    app.run(debug=True)