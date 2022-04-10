from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
import login_app
# import cs304dbi_sqlite3 as dbi

import random

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    #gets session value
    sessvalue = request.cookies.get('session')

    #if there is no session (meaning the user has not logged in) go to main template
    if sessvalue == None:
        return render_template('main.html')
    #if the user is logged in, then go to greet.html (we'll need to change this later but it's just a placeholder for now)
    else:
        return redirect(url_for("greet"))

@app.route('/signup/', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get('email')
        username = request.form.get('username')
        passwd = request.form.get('password')

        conn = dbi.connect()

        row = login_app.insert_user(conn, email, username, passwd)

        if row == (False, True, False):
            flash('duplicate key for username {}'.format(username))
            return redirect( url_for('index'))
        elif row[0] == False and row[1] == False:
            flash('some other error')
            return render_template('signup.html')
    return render_template('signup.html')

@app.route('/login/', methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get('email')
        username = request.form.get('username')
        passwd = request.form.get('password')

        conn = dbi.connect()

        row = login_app.login_user(conn, username, passwd)

        if row == (False, False):
            flash('login incorrect. Try again or join')
            return render_template('login.html')
        else:
            flash('successfully logged in ' + username)
            session['username'] = username
            session['uid'] = row[1]
            session['logged_in'] = True
            session['visits'] = 1
            return redirect( url_for('greet')) #also just a placeholder for now, should redirect somewhere else
    return render_template('login.html')

@app.route('/greet/', methods=["GET", "POST"])
def greet():
    if request.method == 'GET':
        return render_template('greet.html', title='Customized Greeting')
    else:
        try:
            username = request.form['username'] # throws error if there's trouble
            flash('form submission successful')
            return render_template('greet.html',
                                   title='Welcome '+username,
                                   name=username)

        except Exception as err:
            flash('form submission error'+str(err))
            return redirect( url_for('index') )

@app.route('/formecho/', methods=['GET','POST'])
def formecho():
    if request.method == 'GET':
        return render_template('form_data.html',
                               method=request.method,
                               form_data=request.args)
    elif request.method == 'POST':
        return render_template('form_data.html',
                               method=request.method,
                               form_data=request.form)
    else:
        # maybe PUT?
        return render_template('form_data.html',
                               method=request.method,
                               form_data={})

@app.route('/testform/')
def testform():
    # these forms go to the formecho route
    return render_template('testform.html')


@app.before_first_request
def init_db():
    dbi.cache_cnf()
    # set this local variable to 'wmdb' or your personal or team db
    db_to_use = 'studspot_db' 
    dbi.use(db_to_use)
    print('will connect to {}'.format(db_to_use))

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
