from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    print("Handling request to home page.")
    return "I'm gonna be a football app."
