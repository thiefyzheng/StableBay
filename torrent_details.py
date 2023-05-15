import mysql.connector
import json
import mysql.connector

# Database configuration
db_host = 'localhost'
db_user = 'stablebay'
db_password = '6969'
db_name = 'StableDB'

def get_torrent_details(torrent_id):
    # Open database connection
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor(dictionary=True)

    # Retrieve torrent details from the database
    cursor.execute(
        "SELECT models.id, models.name, models.description, models.magnet_link, models.image_link, models.uploaded_by, models.upload_date, categories.id as category_id, categories.name as category FROM models INNER JOIN categories ON models.category = categories.id WHERE models.id = %s",
        (torrent_id,))
    torrent = cursor.fetchone()

    # Retrieve attribute details for the torrent from the database
    cursor.execute("SELECT attributes.name, model_attributes.value FROM attributes INNER JOIN model_attributes ON attributes.id = model_attributes.attribute_id WHERE model_attributes.model_id = %s", (torrent_id,))
    attributes = cursor.fetchall()

    # Close database connection
    cursor.close()
    conn.close()

    # Add attributes to torrent list
    torrent['attributes'] = []
    for attribute in attributes:
        torrent['attributes'].append({'name': attribute['name'], 'value': attribute['value']})

    # Add uploaded_by to attributes
    torrent['attributes'].append({'name': 'Uploaded By', 'value': torrent['uploaded_by']})

    return torrent


def update_torrent(torrent_id, name, description, magnet_link, image_link):
    # Open database connection
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()

    # Update torrent details in the database
    query = "UPDATE models SET name=%s, description=%s, magnet_link=%s, image_link=%s WHERE id=%s"
    params = (name, description, magnet_link, image_link, torrent_id)
    cursor.execute(query, params)

    # Close database connection
    conn.commit()
    cursor.close()
    conn.close()
