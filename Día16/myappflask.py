from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.route("/ver")
def saludar():
    return "<h1>hola mundo</h1>"

@app.route("/hora")
def hora():
    ahora = datetime.now().strftime("%H:%M:%S")
    return f"<h1>la hora es {ahora}</h1>"