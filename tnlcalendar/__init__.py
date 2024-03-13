#!/usr/bin/env python3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    bootstrap = Bootstrap5(app)
    csrf.init_app(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/tnlcalendar/db/tnlcalendar.db'
    # Local development
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tnlcalendar.db'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SECRET_KEY'] = 'thisisadummyvaluereplaceitwithsomethinglikeanenvvar!'
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['REMEMBER_COOKIE_SECURE'] = True

    db.init_app(app)

    with app.app_context():
        from . import routes
        db.create_all()
        return app
