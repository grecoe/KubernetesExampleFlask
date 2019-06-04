#flask_web/app.py

from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return "You made it finally!"


if __name__ == '__main__':
    app.run(debug=True)