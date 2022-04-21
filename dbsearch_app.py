import cs304dbi as dbi
import pymysql

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