import os
import datetime
import json
from flask import Flask, render_template, request, session, redirect
from mysql.connector import connect, Error

app = Flask(__name__)

db_host = 'localhost'
db_user = 'stablebay'
db_password = '5488'
db_name = 'StableDB'


def execute_query(query, params=None, fetchall=False):
    try:
        conn = connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = None
        if fetchall:
            result = cursor.fetchall()
        else:
            result = cursor.fetchone()
        cursor.close()
        conn.commit()
    except Error as e:
        print(f"Error occurred: {e}")
        result = None
    finally:
        if conn.is_connected():
            conn.close()
    return result


@app.route('/torrents/<string:torrent_uuid>', methods=['GET', 'POST'])
def torrent_details(torrent_uuid):
    # Get the torrent details from the database
    query = "SELECT name, description, image_link, magnet_link, uploaded_by, upload_date FROM models WHERE uuid = %s"
    params = (torrent_uuid,)
    result = execute_query(query, params=params)

    # Check if the torrent with the given UUID exists in the database
    if not result:
        return 'Torrent not found', 404

    name, description, image_link, magnet_link, uploaded_by, upload_date = result

    # Handle comment form submission
    if request.method == 'POST':
        if 'username' not in session:
            return 'You must be logged in to submit a comment', 401

        comment = request.form['comment']
        username = session['username']
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Construct the query to insert the new comment into the database
        query = "INSERT INTO comments (torrent_uuid, username, timestamp, comment, upvotes, downvotes) VALUES (%s, %s, %s, %s, 0, 0)"
        params = (torrent_uuid, username, timestamp, comment)

        # Execute the query to insert the new comment into the database
        execute_query(query, params=params)

        # Reload the page to display the new comment
        return redirect(request.url)

    # Load the comments for the torrent from the database
    query = "SELECT id, username, timestamp, comment, upvotes, downvotes FROM comments WHERE torrent_uuid = %s"
    params = (torrent_uuid,)
    result = execute_query(query, params=params, fetchall=True)

    # Sort the comments by the highest upvote - downvote count
    comments = sorted(result, key=lambda x: x[4] - x[5], reverse=True)

    # Render the template with the torrent details and comments
    return render_template('torrent_details.html', name=name, description=description, image_link=image_link,
                           magnet_link=magnet_link, uploaded_by=uploaded_by, upload_date=upload_date, comments=comments)
