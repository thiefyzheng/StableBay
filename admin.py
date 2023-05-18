import mysql.connector
from config import db_password

db_host = 'localhost'
db_user = 'stablebay'
db_name = 'StableDB'

def get_users():
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()
    query = "SELECT * FROM users"
    cursor.execute(query)
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users



def get_user(user_id):
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id=%s"
    cursor.execute(query, (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        columns = [column[0] for column in cursor.description]
        user = dict(zip(columns, row))
        return user
    else:
        return None

def remove_user(user_id):
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()
    query = "DELETE FROM users WHERE id=%s"
    cursor.execute(query, (user_id,))
    conn.commit()
    cursor.close()
    conn.close()

def edit_post(post_id, new_content):
    # Add code here to update the post with the specified ID
    pass

def remove_post(post_id):
    # Add code here to delete the post with the specified ID
    pass

def edit_comment(comment_id, new_content):
    # Add code here to update the comment with the specified ID
    pass

def remove_comment(comment_id):
    # Add code here to delete the comment with the specified ID
    pass

import edit

def is_admin(username):
    # Check if user is in admin database table
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()
    query = "SELECT is_admin FROM users WHERE username=%s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None and result[0]

def edit_user(user_id, new_email=None, new_username=None, new_password=None, new_verified=None, new_verification_code=None, new_reset_token=None, new_bio=None, new_is_admin=None):
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()
    if new_email:
        query = "UPDATE users SET email=%s WHERE id=%s"
        cursor.execute(query, (new_email, user_id))
    if new_username:
        query = "UPDATE users SET username=%s WHERE id=%s"
        cursor.execute(query, (new_username, user_id))
    if new_password:
        query = "UPDATE users SET password=%s WHERE id=%s"
        cursor.execute(query, (new_password, user_id))
    if new_verified is not None:
        query = "UPDATE users SET verified=%s WHERE id=%s"
        cursor.execute(query, (new_verified, user_id))
    if new_verification_code:
        query = "UPDATE users SET verification_code=%s WHERE id=%s"
        cursor.execute(query, (new_verification_code, user_id))
    if new_reset_token:
        query = "UPDATE users SET reset_token=%s WHERE id=%s"
        cursor.execute(query, (new_reset_token, user_id))
    if new_bio:
        query = "UPDATE users SET bio=%s WHERE id=%s"
        cursor.execute(query, (new_bio, user_id))
    if new_is_admin is not None:
        query = "UPDATE users SET is_admin=%s WHERE id=%s"
        cursor.execute(query, (new_is_admin, user_id))
    conn.commit()
    cursor.close()
    conn.close()
