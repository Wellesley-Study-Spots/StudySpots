import cs304dbi as dbi

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