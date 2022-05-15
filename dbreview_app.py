import cs304dbi as dbi
import pymysql

def insert_review(conn, rating, comment, sid, uid):
    '''
    inserts a review into the review table and commits 
    the changes into the database
    '''
    curs = dbi.dict_cursor(conn)

    curs.execute(
        '''
        insert into review(sid, rating, comment, author)
        values (%s, %s, %s, %s)
        ''', [sid, rating, comment, uid]
    )

    conn.commit()

def get_reviews(conn, sid):
    '''
    gets all the review for a spot and returns list of reviews, 
    with each review containg the following values: sid, rating,
    comment, username, rid, and author
    '''
    
    curs = dbi.dict_cursor(conn)

    curs.execute(
        '''
        select sid, rating, comment, username, rid, author
        from review inner join user 
        on (review.author = user.uid)
        where sid = %s
        ''', [sid]
    )

    rows = curs.fetchall()

    return rows

def get_review(conn, rid):
    '''
    selects a reviews from the review table and returns one value:
    the sid of the spot the review is associated with
    '''
    curs = dbi.dict_cursor(conn)

    curs.execute(
        '''
        select sid from review where rid = %s
        ''', [rid]
    )

    row = curs.fetchone()

    return row

def delete_all_reviews(conn, sid):
    '''
    deletes all reviews from a specific spot and 
    commits the changes in the database
    '''
    curs = dbi.dict_cursor(conn)

    curs.execute(
        '''
        delete from review
        where sid = %s
        ''', [sid]
    )

    conn.commit()

def delete_review(conn, rid):
    '''
    deletes a single review from the review table, commits the changes,
    and returns the sid the review was associated with
    '''

    curs = dbi.dict_cursor(conn)

    row = get_review(conn, rid)
    sid = row['sid']

    curs.execute(
        '''
        delete from review
        where rid = %s
        ''', [rid]
    )

    conn.commit()

    return sid



