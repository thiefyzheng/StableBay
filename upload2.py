import mysql.connector
import mysql.connector

import json

from flask import request

# Database configuration
db_host = 'localhost'
db_user = 'stablebay'
db_password = '6969'
db_name = 'StableDB'


def upload2(uuid, category_id, value):
    # Connect to the database
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

    try:
        # Create a cursor to execute queries
        cursor = conn.cursor()

        # Get the model from the database
        query = 'SELECT * FROM models WHERE id = %s'
        cursor.execute(query, (uuid,))
        model = cursor.fetchone()

        if model is None:
            # Model with given UUID not found
            raise ValueError('Model with UUID {} not found'.format(uuid))

        # Find the category name based on the selected ID
        category_name = None
        query = 'SELECT name FROM categories WHERE id = %s'
        cursor.execute(query, (category_id,))
        result = cursor.fetchone()

        if result is not None:
            category_name = result[0]

        if category_name is None:
            # Category with given ID not found
            raise ValueError('Category with ID {} not found'.format(category_id))

        # Get the attributes for the category
        attributes = get_attributes(category_id)

        # Convert the attributes to a dictionary
        attributes_dict = {}
        for attribute in attributes:
            # Get the value for the attribute from the database
            if attribute['name'] == 'value':
                attributes_dict[attribute['name']] = value
            else:
                attr_query = 'SELECT value FROM model_attributes WHERE model_id = %s AND attribute_id = %s'
                cursor.execute(attr_query, (uuid, attribute['id']))
                attr_value = cursor.fetchone()[0]
                attributes_dict[attribute['name']] = attr_value

        # Update the model's category and attributes
        query = 'UPDATE models SET category = %s, attributes = %s WHERE id = %s'
        cursor.execute(query, (category_name, json.dumps(attributes_dict), uuid))
        conn.commit()

        # Return a success message
        return 'Model with UUID {} updated with category {} and attributes {}'.format(uuid, category_name,
                                                                                      attributes_dict)

    finally:
        # Close the database connection
        conn.close()


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

        print(attribute_dicts)  # Add this line to check the attribute_dicts value

        return attribute_dicts

    except Exception as e:
        print(e)
        return None

    finally:
        # Close the database connection
        conn.close()


def add_model_attributes(model_id, attribute_values_json):
    # Convert JSON to dictionary
    attribute_values = json.loads(attribute_values_json)
    print(f"attribute_values: {attribute_values}")

    # Connect to the database
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

    try:
        # Create a cursor to execute queries
        cursor = conn.cursor()

        # Loop through the attributes and insert them into the model_attributes table
        for key, value in attribute_values.items():
            print(f"key: {key}, value: {value}")
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
            print(f"attribute_id: {attribute_id}")

            # Check if value is a list
            if isinstance(value, list):
                # Insert multiple values for the same attribute
                for val in value:
                    query = '''
                    INSERT INTO model_attributes (model_id, attribute_id, value)
                    VALUES (%s, %s, %s)
                    '''
                    cursor.execute(query, (model_id, attribute_id, val))
                    print(f"Inserted row with model_id: {model_id}, attribute_id: {attribute_id}, value: {val}")
            else:
                # Insert a single value for the attribute
                query = '''
                INSERT INTO model_attributes (model_id, attribute_id, value)
                VALUES (%s, %s, %s)
                '''
                cursor.execute(query, (model_id, attribute_id, value))
                print(f"Inserted row with model_id: {model_id}, attribute_id: {attribute_id}, value: {value}")

        # Commit changes to the database
        conn.commit()

    except Exception as e:
        print(e)

    finally:
        # Close the database connection
        conn.close()

