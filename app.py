from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi 
import login_app
import dbsearch_app
import dbreview_app
import os
import random

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

# new for file upload
app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB

@app.route('/')
def index():
    #if the user is logged in, then redirect the user so they do not have to login again
    if 'logged_in' in session:
        return redirect(url_for("homepage"))
    #if the user is not logged in, have them either sign up or login
    else:
        return render_template('main.html', 
                                page_title="StudySpots")

@app.route('/signup/', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get('email')
        username = request.form.get('username')
        passwd = request.form.get('password')

        if len(email) > 25:
            flash('please use a wellesley email address with less than 25 characters in total')
            return render_template('signup.html', 
                                    page_title = "Signup")

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

        #create session
        session['username'] = username
        session['uid'] = row[0]
        session['logged_in'] = True
        session['visits'] = 1
        return redirect(url_for('homepage'))
    else:
        return render_template('signup.html', 
                                page_title="Signup")

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
            return render_template('login.html', 
                                    page_title="Login")
        else:
            #create session
            session['username'] = username
            session['uid'] = row[1]
            session['logged_in'] = True
            session['visits'] = 1
            return redirect( url_for('homepage')) 
    return render_template('login.html', 
                            page_title="Login")


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
    #if the user is not logged in, then redirect the user back to the index
    if 'logged_in' not in session:
        return redirect(url_for("index"))

    if request.method == 'GET':
        # get all study spots 
        conn = dbi.connect()
        spots = dbsearch_app.all_spots_lookup(conn)
        # render them on page
        return render_template('homepage.html', 
                                spots = spots[-9:], 
                                page_title="StudySpots")

@app.route('/addspot/', methods = ["GET", "POST"])
def addspot():
    if request.method == 'GET':
        return render_template('addspot.html', 
                                page_title="Add a New Spot")
    if request.method == 'POST':
        # Grab spot values
        spotname = request.form['spotname']
        description = request.form['description']
        location = request.form['location']
        a = request.form.getlist('amenities')
        amenities = ','.join(a)
        uid = session.get('uid')
        filename = None

        # Add spot without an image so that the spot is associated with an sid
        conn = dbi.connect()
        # add.spot returns sid
        sid = dbsearch_app.add_spot(conn, spotname, description, 
                                    location, amenities, uid, filename)

        # file upload
        f = request.files['pic']
        user_filename = f.filename
        ext = user_filename.split('.')[-1]
        filename = secure_filename('{}.{}'.format(sid,ext))
        pathname = os.path.join(app.config['UPLOADS'],filename)
        f.save(pathname)

        # Add spot with image
        conn = dbi.connect()
        dbsearch_app.edit_spot(conn, spotname, description, 
                                filename, location, amenities, sid)

        #Redirect to individual spot page
        return redirect( url_for('studyspot_lookup', 
                                    sid=sid)) 

@app.route('/pic/<sid>')
def pic(sid):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    row = dbsearch_app.get_photo(conn, sid)
    return send_from_directory(app.config['UPLOADS'],row['photo'])

#Creates the individual study spot page
@app.route('/studyspot/<int:sid>',  methods=["GET"])
def studyspot_lookup(sid):
    conn = dbi.connect()
    studyspot = dbsearch_app.spot_lookup(conn, sid)
    if not studyspot:
        flash('Study spot does not exist')
        return redirect(url_for('homepage'))
    
    title = studyspot['spotname']
    description = studyspot['description']
    location = studyspot['location']
    amenities = studyspot['amenities'].split(",")
    spot_author = studyspot['author']
    uid = session.get('uid')
    filename = studyspot['photo']

    reviews = dbreview_app.get_reviews(conn, sid)

    return render_template('spot.html', 
                            page_title=title, 
                            title=title, 
                            description = description, 
                            location = location, 
                            amenities  = amenities, 
                            sid  = sid, 
                            reviews = reviews, 
                            uid = uid,
                            spot_author = spot_author,
                            filename = filename)

@app.route('/review/<int:sid>', methods=["POST"])
def review(sid):
    conn = dbi.connect()

    #get information from review form
    rating = request.form.get("rating")
    comment = request.form.get("comment")
    uid = session.get('uid')

    dbreview_app.insert_review(conn, rating, comment, sid, uid)

    return redirect(url_for('studyspot_lookup', sid = sid))

@app.route('/edit-spot/<int:sid>', methods = ["GET", "POST"])
def edit_spot(sid):
    conn = dbi.connect()

    if request.method == "GET":

        #prefill form
        row = dbsearch_app.spot_lookup(conn, sid)
        old_description = row['description']
        old_location = row['location']
        old_a = row['amenities']

        return render_template('edit_spot.html', 
                                sid = sid, 
                                spotname = row['spotname'], 
                                description = old_description, 
                                location = old_location, 
                                amenities=old_a, 
                                page_title="Edit spot")
        
    else:
        spotname = request.form['spotname']
        description = request.form['description']
        location = request.form['location']
        a = request.form.getlist('amenities')
        amenities = ','.join(a)

        # file upload
        f = request.files['pic']
        filename = ''

        # if there is a new file
        if len(f.filename) > 0:
            #get the name of the old photo
            row = dbsearch_app.get_photo(conn, sid) 
            photo = row['photo']   

            #only delete if the file exists
            if os.path.exists("uploads/{}".format(photo)):
                os.remove("uploads/{}".format(photo))
            else:
                flash('error occured: unable to delete')
                return redirect(url_for('edit_spot', sid = sid))

            #replace old photo with new photo
            user_filename = f.filename
            ext = user_filename.split('.')[-1]
            filename = secure_filename('{}.{}'.format(sid,ext))
            pathname = os.path.join(app.config['UPLOADS'],filename)
            f.save(pathname)

        # commit changes to the databases
        conn = dbi.connect()
        dbsearch_app.edit_spot(conn, spotname, description, 
                                filename, location, amenities, sid)

        return redirect(url_for('studyspot_lookup', sid = sid))
    
@app.route('/delete-spot/<int:sid>', methods = ["POST"])
def delete_spot(sid):
    conn = dbi.connect()

    #get the name of the photo
    row = dbsearch_app.get_photo(conn, sid) 
    photo = row['photo']   

    #only delete if the file exists
    if os.path.exists("uploads/{}".format(photo)):
        os.remove("uploads/{}".format(photo))
    else:
        flash('error occured: unable to delete')
        return redirect(url_for('studyspot_lookup', sid = sid))

    dbsearch_app.delete_spot(conn, sid)
    flash('successfully deleted spot')
    return redirect(url_for('homepage'))

@app.route('/delete-review/<int:rid>', methods = ["POST"])
def delete_review(rid):
    conn = dbi.connect()

    sid = dbreview_app.delete_review(conn, rid)

    return redirect(url_for('studyspot_lookup', sid = sid))

@app.route('/search/', methods=["GET"])
def search():
    conn = dbi.connect()

    kind = request.args.get("kind")
    query = request.args.get("search")

    rows = dbsearch_app.search(conn, kind, query)

    return render_template('search.html', 
                            rows = rows, 
                            query = query, 
                            page_title="Search results")

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
