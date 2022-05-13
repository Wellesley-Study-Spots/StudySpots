import cs304dbi as dbi
import pymysql
import dbreview_app


def spot_lookup(conn, sid):
    '''
    selects a spot in the spot table and returns five values:
    the spotname, description, location, amenities, and author
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute(
        '''select spotname, description, photo, location, amenities, author
        from spot
        where sid = %s''', [sid]
    )
    spot = curs.fetchone()
    return spot


def add_spot(conn, spotname, description, location, amenities, uid, filename):
    '''
    inserts a spot to a database and returns the spot's sid
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute(
        '''insert into spot(spotname, description, location, amenities, author, photo)
            values(%s, %s, %s, %s, %s, %s)
            on duplicate key update photo = %s
        ''', [spotname, description, location, amenities, uid, filename, filename]
    )
    conn.commit()
    curs.execute('select last_insert_id()')
    row = curs.fetchone()

    return (row['last_insert_id()']) 


def all_spots_lookup(conn):
    ''' 
    selects all of the spots in the database and returns a list of dictionaries 
    with the following 3 values: spotname, location, sid
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select spotname, location, sid
        from spot
        order by sid''' )
    spots = curs.fetchall()
    return spots

def search(conn, kind, query):
    '''
    select spots in the database depending on the kind and the query.
    
    if location is selected, it will return
    a list of dictionaries that contain the following values:
    spotname, location, sid, and description

    if name is selected, it will return a list of dictionaries
    that contain the following values: spotname, location, sid,
    and description
    '''
    curs = dbi.dict_cursor(conn)

    rows = None
    if kind == 'location':
        curs.execute(
            '''
            select spotname, location, sid, description
            from spot
            where location like %s
            ''', ["%" + query + "%"]
        )
        rows = curs.fetchall()
        return rows
    else:
        curs.execute(
            '''
            select spotname, location, sid, description
            from spot
            where spotname like %s
            ''', "%" + query + "%"
        )
        rows = curs.fetchall()
        return rows

def edit_spot(conn, spotname, description, filename, location, amenities, sid):
    '''
    updates a spot in the database and commits the changes to the database
    '''

    curs = dbi.dict_cursor(conn)

    curs.execute(
        '''
        update spot 
        set spotname = %s, description = %s, location = %s, amenities = %s
        where sid = %s
        ''', [spotname, description, location, amenities, sid]
    )

    conn.commit()

    #only commit chnages to the database if there is a new file
    if len(str(filename)) > 0:
        curs.execute(
            '''
            update spot set photo = %s where sid=%s
            ''', [filename, sid]
        )

        conn.commit()


def delete_spot(conn, sid):
    '''
    deletes a spot in the spot table and 
    commits the changes in the database
    '''

    curs = dbi.dict_cursor(conn)

    dbreview_app.delete_all_reviews(conn, sid)

    curs.execute(
        '''
        delete from spot
        where sid = %s
        ''', [sid]
    )

    conn.commit()

def get_photo(conn, sid):
    '''
    gets the photo from the spot table and returns
    the name of the photo
    '''
    curs = dbi.dict_cursor(conn)

    curs.execute(
        '''select photo from spot where sid = %s''',
        [sid])

    row = curs.fetchone()
    return row

