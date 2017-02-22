import flask
import flask_sqlalchemy import SQLAlchemy

class sqldb(object):
    def __init__(self, flaskApp):
        self.db = SQLAlchemy(flaskApp)