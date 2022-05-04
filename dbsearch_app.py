import cs304dbi as dbi
import pymysql
import dbreview_app


def spot_lookup(conn, sid):
    '''
    selects a spot in the spot table and returns four values:
    the spotname, description, location, and amenities
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute(
        '''select spotname, description, location, amenities
        from spot
        where sid = %s''', [sid]
    )
    spot = curs.fetchone()
    return spot


def add_spot(conn, spotname, description, location, amenities, uid):
    '''
    inserts a spot to a database and returns the spot's sid
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute(
        '''insert into spot(spotname, description, location, amenities, author)
            values(%s, %s, %s, %s, %s)
        ''', [spotname, description, location, amenities, uid]
    )
    conn.commit()
    curs.execute('select last_insert_id()')
    row = curs.fetchone()

    return (row['last_insert_id()']) 


def all_spots_lookup(conn):
    ''' 
    selects all of the spots in the database and returns 8 values:
    sid, author, spotname, description, location, amenities, status,
    and photo
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select *
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

def edit_spot(conn, spotname, description, location, amenities, sid):
    '''
    updates a spot in the database and commits the changes to the database
    '''

    curs = dbi.dict_cursor(conn)

    if len(spotname) > 0:
        curs.execute(
            '''
            update spot set spotname = %s where sid=%s
            ''', [spotname, sid]
        )
        
        conn.commit()

    
    if len(description) > 0:
        curs.execute(
            '''
            update spot set description = %s where sid=%s
            ''', [description, sid]
        )

        conn.commit()


    if len(location) > 0:
        curs.execute(
            '''
            update spot set location = %s where sid=%s
            ''', [location, sid]
        )

        conn.commit()


    if len(amenities) > 0:
        curs.execute(
            '''
            update spot set amenities = %s where sid=%s
            ''', [amenities, sid]
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



