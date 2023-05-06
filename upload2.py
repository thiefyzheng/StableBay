import json
import mysql.connector

# Database configuration
db_host = 'localhost'
db_user = 'stablebay'
db_password = '5488'
db_name = 'StableDB'


def upload2(uuid, category_id):
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
            attributes_dict[attribute['name']] = attribute['value_type']

        # Update the model's category and attributes
        query = 'UPDATE models SET category = %s, attributes = %s WHERE id = %s'
        cursor.execute(query, (category_name, json.dumps(attributes_dict), uuid))
        conn.commit()

        # Return a success message
        return 'Model with UUID {} updated with category {} and attributes {}'.format(uuid, category_name, attributes_dict)

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
        SELECT a.name, a.value_type
        FROM category_attributes ca
        JOIN attributes a ON ca.attribute_id = a.id
        WHERE ca.category_id = %s
        '''
        cursor.execute(query, (category_id,))
        attributes = cursor.fetchall()

        # Convert the list of tuples to a list of dictionaries
        attribute_dicts = []
        for attribute in attributes:
            attribute_dict = {'name': attribute[0], 'value_type': attribute[1]}
            attribute_dicts.append(attribute_dict)

        return attribute_dicts

    except Exception as e:
        print(e)  # add a print statement to check the exception
        return None

    finally:
        # Close the database connection
        conn.close()


