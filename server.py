import flask
import flask_sqlalchemy
import flask_restless

# Create the Flask application and the Flask-SQLAlchemy object.
app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
db = flask_sqlalchemy.SQLAlchemy(app)

def post_preprocessor(data=None, **kw):
    """Accepts a single argument, `data`, which is the dictionary of
    fields to set on the new instance of the model.

    """
    print '================================'
    print 'Data:', data
    print '\tType Of:', type(data)
    print 'kw:', kw
    print '\tType Of:', type(kw)
    print kw[0]
    pass


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
    data = db.Column(db.Text)
    acc = db.Column(db.Float)
    loss = db.Column(db.Float)
    val_acc = db.Column(db.Float)
    val_loss = db.Column(db.Float)
    
# Create the database tables.
db.create_all()

# Create the Flask-Restless API manager.
manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Person, methods=['GET', 'POST', 'DELETE'])
manager.create_api(Article, methods=['GET'])

manager.create_api(kerasdata, methods=['GET', 'POST'],  preprocessors={'POST':[post_preprocessor]})

# start the flask loop
app.run(host='0.0.0.0')