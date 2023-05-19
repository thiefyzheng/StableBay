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


def get_comment(comment_id):
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()
    query = "SELECT id, comment, user_id, torrent_id FROM comments WHERE id=%s"
    params = (comment_id,)
    cursor.execute(query, params)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        comment = {
            'id': result[0],
            'comment': result[1],
            'user_id': result[2],
            'torrent_id': result[3]
        }
        return comment
    else:
        return None


def upvote_comment(user_id, comment_id):
    # Connect to the database
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()

    # Check if the user has already upvoted this comment
    query = "SELECT * FROM comment_votes WHERE user_id=%s AND comment_id=%s"
    cursor.execute(query, (user_id, comment_id))
    result = cursor.fetchall()
    if result:
        # The user has already upvoted this comment
        # Decrement the upvotes count for the comment
        query = "UPDATE comments SET upvotes=upvotes-1 WHERE id=%s"
        cursor.execute(query, (comment_id,))
        # Delete the record in the comment_votes table to track that the user has removed their upvote
        query = "DELETE FROM comment_votes WHERE user_id=%s AND comment_id=%s"
        cursor.execute(query, (user_id, comment_id))
        print("Upvote removed successfully")
    else:
        # The user has not upvoted this comment yet
        # Check if the user has already downvoted this comment
        query = "SELECT * FROM comment_votes WHERE user_id=%s AND comment_id=%s AND vote=-1"
        cursor.execute(query, (user_id, comment_id))
        result = cursor.fetchall()
        if result:
            # The user has already downvoted this comment
            # Do not allow the user to upvote and downvote at the same time
            print("Cannot upvote and downvote at the same time")
        else:
            # The user has not downvoted this comment yet
            # Increment the upvotes count for the comment
            query = "UPDATE comments SET upvotes=upvotes+1 WHERE id=%s"
            cursor.execute(query, (comment_id,))
            # Insert a record in the comment_votes table to track that the user has upvoted this comment
            query = "INSERT INTO comment_votes (user_id, comment_id, vote) VALUES (%s, %s, 1)"
            cursor.execute(query, (user_id, comment_id))
            print("Upvoted successfully")

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()


def downvote_comment(user_id, comment_id):
    # Connect to the database
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()

    # Check if the user has already downvoted this comment
    query = "SELECT * FROM comment_votes WHERE user_id=%s AND comment_id=%s AND vote=-1"
    cursor.execute(query, (user_id, comment_id))
    result = cursor.fetchall()
    if result:
        # The user has already downvoted this comment
        # Decrement the downvotes count for the comment
        query = "UPDATE comments SET downvotes=downvotes-1 WHERE id=%s"
        cursor.execute(query, (comment_id,))
        # Delete the record in the comment_votes table to track that the user has removed their downvote
        query = "DELETE FROM comment_votes WHERE user_id=%s AND comment_id=%s AND vote=-1"
        cursor.execute(query, (user_id, comment_id))
        print("Downvote removed successfully")
    else:
        # The user has not downvoted this comment yet
        # Check if the user has already upvoted this comment
        query = "SELECT * FROM comment_votes WHERE user_id=%s AND comment_id=%s AND vote=1"
        cursor.execute(query, (user_id, comment_id))
        result = cursor.fetchall()
        if result:
            # The user has already upvoted this comment
            # Do not allow the user to upvote and downvote at the same time
            print("Cannot upvote and downvote at the same time")
        else:
            # The user has not upvoted this comment yet
            # Increment the downvotes count for the comment
            query = "UPDATE comments SET downvotes=downvotes+1 WHERE id=%s"
            cursor.execute(query, (comment_id,))
            # Insert a record in the comment_votes table to track that the user has downvoted this comment
            query = "INSERT INTO comment_votes (user_id, comment_id, vote) VALUES (%s, %s, -1)"
            cursor.execute(query, (user_id, comment_id))
            print("Downvoted successfully")

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()
