import flask
from flask import request, json
from flask_sqlalchemy import SQLAlchemy

from startup import db, app


@app.route('/push/epoch', methods=['GET', 'POST'])
def epoch_push():
    if request.method == 'POST':
        if request.headers['Content-Type'] == 'application/json':
            print json.dumps(request.json)
    else:
        show_the_login_form()


# start the flask loop
app.run(host='0.0.0.0')