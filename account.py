import mysql.connector

# Database configuration
db_host = 'localhost'
db_user = 'stablebay'
db_password = '6969'
db_name = 'StableDB'

def get_user_torrents(username):
    # Connect to the database
    cnx = mysql.connector.connect(user=db_user, password=db_password,
                                  host=db_host, database=db_name)
    cursor = cnx.cursor(dictionary=True)

    # Execute the query
    query = "SELECT * FROM models WHERE uploaded_by = %s"
    cursor.execute(query, (username,))
    models = cursor.fetchall()

    # Close the database connection
    cursor.close()
    cnx.close()

    return models

