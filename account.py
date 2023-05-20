import mysql.connector
from config import db_password
# Database configuration
db_host = 'localhost'
db_user = 'stablebay'

db_name = 'StableDB'

def get_user_torrents(username):
    # Connect to the database
    cnx = mysql.connector.connect(user=db_user, password=db_password, host=db_host, database=db_name)
    cursor = cnx.cursor(dictionary=True)

    # Execute the query to get the user's torrents
    query = "SELECT * FROM models WHERE uploaded_by = %s"
    cursor.execute(query, (username,))
    models = cursor.fetchall()

    # Execute another query to get the user's bio
    query = "SELECT bio FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    bio = cursor.fetchone()['bio']

    # Close the database connection
    cursor.close()
    cnx.close()

    # Return both the torrents and the bio
    return models, bio
