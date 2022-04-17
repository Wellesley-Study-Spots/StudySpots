import cs304dbi as dbi

# Gets all of the spots in the database
def all_spots_lookup(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select *
        from spot
        order by sid''' )
    spots = curs.fetchall()
    return spots