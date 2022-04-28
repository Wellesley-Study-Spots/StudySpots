from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi # question - do we want this to be studspot_db as dbi?
import login_app
import dbsearch_app
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

    #if the user is logged in, then redirect the user so they do not have to login again
    if 'logged_in' in session:
        return redirect(url_for("homepage.html"))
    #if the user is not logged in, have them either sign up or login
    else:
        return render_template('main.html')


@app.route('/signup/', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get('email')
        username = request.form.get('username')
        passwd = request.form.get('password')

        conn = dbi.connect()

        row = login_app.insert_user(conn, email, username, passwd)

        #if the username already exists
        if row == (False, True, False):
            flash('duplicate key for username {}'.format(username))
            return render_template('signup.html')
        #if there was some other error
        elif row[0] == False and row[1] == False:
            flash('some other error')
            return render_template('signup.html')
        return redirect(url_for('homepage'))
    else:
        return render_template('signup.html')

@app.route('/login/', methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get('email')
        username = request.form.get('username')
        passwd = request.form.get('password')

        conn = dbi.connect()

        row = login_app.login_user(conn, username, passwd)

        #if the login information was incorrect
        if row == (False, False):
            flash('login incorrect. Try again or join')
            return render_template('login.html')
        else:
            #create session
            session['username'] = username
            session['uid'] = row[1]
            session['logged_in'] = True
            session['visits'] = 1
            return redirect( url_for('homepage')) 
    return render_template('login.html')


@app.route('/logout/')
def logout():
    #if they are logged in
    if 'username' in session:
        #remove session
        username = session['username']
        session.pop('username')
        session.pop('uid')
        session.pop('logged_in')
        flash('You are logged out')
        return redirect(url_for('index'))
    else:
        flash('you are not logged in. Please login or join')
        return redirect( url_for('index') )

@app.route('/homepage/', methods = ["GET"])
def homepage():
    if request.method == 'GET':
        # get all study spots 
        conn = dbi.connect()
        spots = dbsearch_app.all_spots_lookup(conn)
        # render them on page
        return render_template('homepage.html', spots = spots[-3:])

@app.route('/addspot/', methods = ["GET", "POST"])
def addspot():
    if request.method == 'GET':
        return render_template('addspot.html')
    if request.method == 'POST':
        # Grab spot values
        spotname = request.form['spotname']
        description = request.form['description']
        location = request.form['location']
        a = request.form.getlist('amenities')
        amenities = ','.join(a)
        uid = session.get('uid')

        #Add spot
        conn = dbi.connect()
        sid = dbsearch_app.add_spot(conn, spotname, description, location, amenities, uid)

        #Redirect to individual spot page
        return redirect( url_for('studyspot_lookup', sid=sid)) 


#Creates the individual study spot page
@app.route('/studyspot/<int:sid>',  methods=["GET", "POST"])
def studyspot_lookup(sid):
    conn = dbi.connect()
    if request.method == 'GET':
        studyspot = dbsearch_app.spot_lookup(conn, sid)
        if not studyspot:
            flash('Study spot does not exist')
            return redirect(url_for('homepage'))
        
        title = studyspot['spotname']
        description = studyspot['description']
        location = studyspot['location']
        amenities = studyspot['amenities'].split(",")
        
        return render_template('spot.html', title=title, description = description, location = location, amenities  = amenities)
    else:
        return render_template('spot.html', title=title, description = description, location = location, amenities  = amenities)


@app.route('/search/', methods=["GET"])
def search():
    conn = dbi.connect()

    kind = request.args.get("kind")
    query = request.args.get("search")

    rows = dbsearch_app.search(conn, kind, query)

    return render_template('search.html', rows = rows, query = query)

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
