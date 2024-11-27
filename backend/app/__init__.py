from flask import Flask
from flask_pymongo import PyMongo

mongo = None

def create_app():
    global mongo
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    mongo = PyMongo(app)
    
    from .routes import abonne_bp
    app.register_blueprint(abonne_bp, url_prefix='/api')
    
    return app, mongo
