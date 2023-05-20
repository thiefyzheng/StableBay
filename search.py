import json
import mysql.connector
from config import db_password
# Database configuration
db_host = 'localhost'
db_user = 'stablebay'

db_name = 'StableDB'


def search_torrents(query, category, limit=16, offset=0):
 # Establish database connection
 conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

 cursor = conn.cursor()

 # Define query to search for torrents by name, description, category, and NSFW flag
 sql_query = """
 SELECT m.id, m.name, m.uploaded_by, m.image_link, m.upload_date, c.name, m.nsfw
 FROM models m
 JOIN categories c ON m.category = c.id
 WHERE (m.name LIKE %s OR m.description LIKE %s)
 """

 if category:
  sql_query += " AND m.category = %s"
  cursor.execute(sql_query + " LIMIT %s OFFSET %s", ('%' + query + '%', '%' + query + '%', category, limit, offset))
 else:
  cursor.execute(sql_query + " LIMIT %s OFFSET %s", ('%' + query + '%', '%' + query + '%', limit, offset))

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
   'category': result[5],
   'nsfw': bool(result[6])
  }
  torrents.append(torrent)

 # Return the results as a JSON object
 return json.dumps(torrents)
