import json
import mysql.connector


# Database configuration
db_host = 'localhost'
db_user = 'stablebay'
db_password = '6969'
db_name = 'StableDB'


def get_torrents(limit=10):
    # Establish database connection
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

    cursor = conn.cursor()

    # Define query to get torrent information, uploader name, and category name
    query = """
        SELECT m.id, m.name, m.uploaded_by, m.image_link, m.upload_date, c.name
        FROM models m
        JOIN categories c ON m.category = c.id
        ORDER BY m.upload_date DESC
        LIMIT %s;
    """

    # Execute query and retrieve results
    cursor.execute(query, (limit,))
    results = cursor.fetchall()

    # Close database connection
    cursor.close()
    conn.close()

    # Convert the results to a JSON object
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
        print(torrent)
        torrents.append(torrent)

    return json.dumps(torrents)
