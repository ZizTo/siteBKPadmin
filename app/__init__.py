from flask import Flask


app = Flask(__name__)

app.config['SECRET_KEY'] = 'd949d662627f9b4f0e479db5850fdc4c'

from app import routes
