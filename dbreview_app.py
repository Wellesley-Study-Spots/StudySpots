import cs304dbi as dbi
import pymysql

def insert_review(conn, rating, comment, sid, uid):
    curs = dbi.dict_cursor(conn)

    curs.execute(
        '''
        insert into review(sid, rating, comment, author)
        values (%s, %s, %s, %s)
        ''', [sid, rating, comment, uid]
    )

    conn.commit()

def get_reviews(conn, sid):
    curs = dbi.dict_cursor(conn)

    curs.execute(
        '''
        select sid, rating, comment, username
        from review inner join user 
        on (review.author = user.uid)
        where sid = %s
        ''', [sid]
    )

    rows = curs.fetchall()

    return rows; 