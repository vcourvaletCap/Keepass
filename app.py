from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/gestionnaire')
def gestionnaire():
    return render_template('gestionnaire.html')

@app.route('/export')
def export():
    return render_template('exportation.html')

if __name__ == '__main__':
    app.run(debug=True)