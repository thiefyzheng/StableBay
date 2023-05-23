import mysql.connector
from config import db_password

# Database configuration
db_host = 'localhost'
db_user = 'stablebay'
db_name = 'StableDB'


def connect_to_db():
    # Connect to the database
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    # Create a cursor to execute queries
    cursor = conn.cursor()
    return conn, cursor


def close_db_connection(conn):
    # Commit the changes and close the database connection
    conn.commit()
    conn.close()


def edit_torrent(id, name=None, image_link=None, description=None):
    conn, cursor = connect_to_db()
    if name:
        cursor.execute("UPDATE models SET name=%s WHERE id=%s", (name, id))
    if image_link:
        cursor.execute("UPDATE models SET image_link=%s WHERE id=%s", (image_link, id))
    if description:
        cursor.execute("UPDATE models SET description=%s WHERE id=%s", (description, id))
    close_db_connection(conn)


def edit_attribute_value(model_id, attribute_name, value):
    conn, cursor = connect_to_db()
    attribute_id_query = "SELECT id FROM attributes WHERE name=%s"
    cursor.execute(attribute_id_query, (attribute_name,))
    attribute_id = cursor.fetchone()[0]

    query = "UPDATE model_attributes SET value=%s WHERE model_id=%s AND attribute_id=%s"
    cursor.execute(query, (value, model_id, attribute_id))
    close_db_connection(conn)


def add_attribute(model_id, attribute_name):
    conn, cursor = connect_to_db()
    attribute_id_query = "SELECT id FROM attributes WHERE name=%s"
    cursor.execute(attribute_id_query, (attribute_name,))
    attribute_id = cursor.fetchone()[0]

    query = "INSERT INTO model_attributes (model_id, attribute_id) VALUES (%s,%s)"
    cursor.execute(query, (model_id, attribute_id))


def remove_attribute(model_id, attribute_name):
    conn, cursor = connect_to_db()

    attribute_id_query = "SELECT id FROM attributes WHERE name=%s"
    cursor.execute(attribute_id_query, (attribute_name,))

    attribute_id = cursor.fetchone()[0]

    query = "DELETE FROM model_attributes WHERE model_id=%s AND attribute_id=%s"


def get_current_values(model_id):
    conn, cursor = connect_to_db()

    query = "SELECT name,image_link,description FROM models WHERE id=%s"
    cursor.execute(query, (model_id,))
    result = cursor.fetchone()

    current_values = {
        'name': result[0],
        'image_link': result[1],
        'description': result[2],
        'attributes': {}
    }

    attributes_query = "SELECT attributes.name,model_attributes.value FROM model_attributes JOIN attributes ON model_attributes.attribute_id=attributes.id WHERE model_attributes.model_id=%s"
    cursor.execute(attributes_query, (model_id,))
    for row in cursor:
        current_values['attributes'][row[0]] = row[1]

    close_db_connection(conn)
    return current_values
