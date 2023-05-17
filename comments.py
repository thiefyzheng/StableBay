import mysql.connector
from config import db_password

db_host = 'localhost'
db_user = 'stablebay'
db_name = 'StableDB'

def add_comment(torrent_id, user_id, comment):
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()
    query = "INSERT INTO comments (torrent_id, user_id, comment) VALUES (%s, %s, %s)"
    params = (torrent_id, user_id, comment)
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close()

def delete_comment(comment_id):
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()
    query = "DELETE FROM comments WHERE id=%s"
    params = (comment_id,)
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close()

def edit_comment(comment_id, new_comment):
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()
    query = "UPDATE comments SET comment=%s WHERE id=%s"
    params = (new_comment, comment_id)
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close()

def upvote_comment(comment_id):
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()
    query = "UPDATE comments SET upvotes=upvotes+1 WHERE id=%s"
    params = (comment_id,)
    cursor.execute(query,params)
    conn.commit()
    cursor.close()
    conn.close()

def downvote_comment(comment_id):
    conn = mysql.connector.connect(host=db_host,user=db_user,password=db_password,database=db_name)
    cursor=conn.cursor()
    query="UPDATE comments SET downvotes=downvotes+1 WHERE id=%s"
    params=(comment_id,)
    cursor.execute(query,params)
    conn.commit()
    cursor.close()
    conn.close()

