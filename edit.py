import mysql.connector
from flask import Flask, request, session
import datetime
import uuid
import json

app = Flask(__name__)

# Database configuration
db_host = 'localhost'
db_user = 'stablebay'
db_password = '6969'
db_name = 'StableDB'


# Function to execute queries on MySQL
def execute_query(query, params=None, fetchall=False):
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetchall:
        result = cursor.fetchall()
    else:
        result = cursor.fetchone()
    # Consume any remaining unread results
    while cursor.nextset():
        pass
    conn.commit()
    conn.close()
    return result


def get_categories():
    # Connect to the database
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

    try:
        # Create a cursor to execute queries
        cursor = conn.cursor()

        # Get the categories from the database
        query = 'SELECT id, name FROM categories'
        cursor.execute(query)
        categories = cursor.fetchall()

        # Return the categories
        return categories

    finally:
        # Close the database connection
        conn.close()


def get_attributes(category_id):
    # Connect to the database
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

    try:
        # Create a cursor to execute queries
        cursor = conn.cursor()

        # Join the category_attributes and attributes tables to get the attributes for the given category ID
        query = '''
        SELECT a.name, a.value_type, ca.is_required
        FROM category_attributes ca
        JOIN attributes a ON ca.attribute_id = a.id
        WHERE ca.category_id = %s
        '''
        cursor.execute(query, (category_id,))
        attributes = cursor.fetchall()

        # Convert the list of tuples to a list of dictionaries
        attribute_dicts = []
        for attribute in attributes:
            attribute_dict = {'name': attribute[0], 'value_type': attribute[1], 'required': attribute[2]}
            attribute_dicts.append(attribute_dict)

        return attribute_dicts

    finally:
        # Close the database connection
        conn.close()


def add_model_attributes(model_id, attribute_values_json):
    # Convert JSON to dictionary
    attribute_values = json.loads(attribute_values_json)

    # Connect to the database
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

    try:
        # Create a cursor to execute queries
        cursor = conn.cursor()

        # Loop through the attributes and insert them into the model_attributes table
        for key, value in attribute_values.items():
            # Get the attribute ID
            query = '''
            SELECT id FROM attributes
            WHERE name = %s
            '''
            cursor.execute(query, (key,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"Attribute {key} not found in attributes table")
            attribute_id = row[0]

            # Insert the attribute value into the model_attributes table
            query = '''
            INSERT INTO model_attributes (model_id, attribute_id, value)
            VALUES (%s, %s, %s)
            '''
            cursor.execute(query, (model_id, attribute_id, value))

            # Commit changes to the database
            conn.commit()

    finally:
        # Close the database connection
        conn.close()


def edit_model(model_id, model_name=None, short_description=None, magnet_link=None, image_link=None, category=None,
 attributes=None):
    if model_name is not None:
        query = "UPDATE models SET name=%s WHERE id=%s"
        params = (model_name, model_id)
        execute_query(query, params)
    if short_description is not None:
        query = "UPDATE models SET description=%s WHERE id=%s"
        params = (short_description, model_id)
        execute_query(query, params)
        print("Description updated")
    if magnet_link is not None:
        query = "UPDATE models SET magnet_link=%s WHERE id=%s"
        params = (magnet_link, model_id)
        execute_query(query, params)
    if image_link is not None:
        query = "UPDATE models SET image_link=%s WHERE id=%s"
        params = (image_link, model_id)
        execute_query(query, params)
    if category is not None:
        query = "UPDATE models SET category=%s WHERE id=%s"
        params = (category, model_id)
        execute_query(query, params)

    if attributes is not None:
        for key, value in attributes.items():
            # Check if attribute value is blank
            if value.strip() == '':
                continue

            query = "SELECT id FROM attributes WHERE name=%s"
            params = (key,)
            row = execute_query(query, params)
            if row is None:
                raise ValueError(f"Attribute {key} not found in attributes table")
            attribute_id = row[0]

            query = "INSERT INTO model_attributes (model_id ,attribute_id ,value) VALUES (%s,%s,%s)"
            params = (model_id, attribute_id, value)
            execute_query(query, params)
