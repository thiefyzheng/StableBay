import mysql.connector
from config import db_password
from comments import add_comment, delete_comment, edit_comment, upvote_comment, downvote_comment

db_host = 'localhost'
db_user = 'stablebay'
db_name = 'StableDB'


def get_torrent_details(torrent_id):
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor(dictionary=True)

    # Retrieve torrent details from the database
    cursor.execute(
        "SELECT models.id, models.name, models.description, models.magnet_link, models.image_link, models.uploaded_by, models.upload_date, categories.id as category_id, categories.name as category FROM models INNER JOIN categories ON models.category = categories.id WHERE models.id = %s",
        (torrent_id,))
    torrent = cursor.fetchone()

    # Retrieve attribute details for the torrent from the database
    cursor.execute(
        "SELECT attributes.name, model_attributes.value FROM attributes INNER JOIN model_attributes ON attributes.id = model_attributes.attribute_id WHERE model_attributes.model_id = %s",
        (torrent_id,))
    attributes = cursor.fetchall()

    # Retrieve comments for the torrent from the database
    cursor.execute("SELECT * FROM comments WHERE torrent_id=%s", (torrent_id,))
    comments = cursor.fetchall()

    # Close database connection
    cursor.close()
    conn.close()

    # Add attributes to torrent list
    torrent['attributes'] = []
    for attribute in attributes:
        torrent['attributes'].append({'name': attribute['name'], 'value': attribute['value']})

    # Add uploaded_by to attributes
    torrent['attributes'].append({'name': 'Uploaded By', 'value': torrent['uploaded_by']})

    # Add comments to torrent list
    torrent['comments'] = []
    for comment in comments:
        comment_dict = {
            'id': comment['id'],
            'user_id': comment['user_id'],
            'comment': comment['comment'],
            'upvotes': comment['upvotes'],
            'downvotes': comment['downvotes'],
            'created_at': comment['created_at']
        }
        torrent['comments'].append(comment_dict)

    return torrent



def update_torrent(torrent_id, name, description, magnet_link, image_link):
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()

    query = "UPDATE models SET name=%s, description=%s,magnet_link=%s,image_link=%s WHERE id=%s"
    params = (name, description, magnet_link, image_link, torrent_id)

    cursor.execute(query, params)

    conn.commit()
    cursor.close()
    conn.close()
