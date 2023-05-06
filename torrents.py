import mysql.connector

TORRENTS_DIR = "/home/stablebay/uploads"
db_host = 'localhost'
db_user = 'stablebay'
db_password = '5488'
db_name = 'StableDB'

def execute_query(query, params=None, fetchall=False):
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = None
    if fetchall:
        result = cursor.fetchall()
    else:
        result = cursor.fetchone()
    cursor.close()
    conn.commit()
    conn.close()
    return result

def get_torrents():
    query = "SELECT id, name, description, file_path, tags, uploaded_by, upload_date FROM models"
    result = execute_query(query, fetchall=True)
    torrents = []
    for row in result:
        torrent_id, name, description, file_path, tags, uploaded_by, upload_date = row
        tags = tags.split(', ')
        torrent = {
            "id": torrent_id,
            "name": name,
            "description": description,
            "file_path": file_path,
            "tags": tags,
            "uploaded_by": uploaded_by,
            "upload_date": upload_date,
            "magnet_button": "",
        }
        torrents.append(torrent)
    return torrents
