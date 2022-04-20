import cs304dbi as dbi
import pymysql

def spot_lookup(conn, sid):
    '''
    gets a spot in the database 
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute(
        '''select * 
        from spot
        where sid = %s''', [sid]
    )
    spot = curs.fetchone()
    return spot


def add_spot(conn, spotname, description, location, amenities, uid):
    '''
    adds a spot to a database 
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
    gets all of the spots in the database
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select *
        from spot
        order by sid''' )
    spots = curs.fetchall()
    return spots