import mysql.connector
import json

# Database configuration
db_host = 'localhost'
db_user = 'stablebay'
db_password = '6969'
db_name = 'StableDB'


def search_torrents(query):
    # Establish database connection
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

    cursor = conn.cursor()

    # Define query to search for torrents by name and description
    sql_query = """
        SELECT m.id, m.name, m.uploaded_by, m.image_link, m.upload_date, c.name
        FROM models m
        JOIN categories c ON m.category = c.id
        WHERE m.name LIKE %s OR m.description LIKE %s
        ORDER BY m.upload_date DESC
    """

    # Execute query with wildcard characters to allow partial matching
    cursor.execute(sql_query, ('%' + query + '%', '%' + query + '%',))

    # Fetch results
    results = cursor.fetchall()

    # Close database connection
    cursor.close()
    conn.close()

    # Convert results to a list of JSON objects
    torrents = []
    for result in results:
        torrent = {
            'id': result[0],
            'name': result[1],
            'uploaded_by': result[2],
            'image_url': result[3],
            'upload_date': str(result[4]),
            'category': result[5]
        }
        torrents.append(torrent)

    # Print the received query and search results


    # Return the results as a JSON object
    return json.dumps(torrents)
