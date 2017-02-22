import flask
from flask_sqlalchemy import SQLAlchemy

# Create the Flask application and the Flask-SQLAlchemy object.
app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
db = SQLAlchemy(app)

# Create your Flask-SQLALchemy models as usual but with the following
# restriction: they must have an __init__ method that accepts keyword
# arguments for all columns (the constructor in
# flask_sqlalchemy.SQLAlchemy.Model supplies such a method, so you
# don't need to declare a new one).
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    age = db.Column(db.Integer)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode)
    published_at = db.Column(db.DateTime)
    author_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    author = db.relationship(Person, backref=db.backref('articles',
                                                        lazy='dynamic'))

class kerasdata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    epoch = db.Column(db.Integer)
    data2 = db.Column(db.Text)
    acc = db.Column(db.Float)
    loss = db.Column(db.Float)
    val_acc = db.Column(db.Float)
    val_loss = db.Column(db.Float)



class KerasModel(db.Model):
    uuid = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.Text)

class KerasEpoch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_uuid = db.Column(db.String(32), db.ForeignKey('kerasmodel.uuid'))
    model_major = db.Column(db.Integer)
    internal_epoch = db.Column(db.Float)
    apparent_epoch = db.Column(db.Integer)

    
# Create the database tables.
db.create_all()