import mysql.connector

# Database configuration
db_host = 'localhost'
db_user = 'stablebay'
db_password = '6969'
db_name = 'StableDB'

# Connect to the database
conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

# Create a cursor to execute queries
cursor = conn.cursor()

# Create the users table if it doesn't exist yet
cursor.execute('''
 CREATE TABLE IF NOT EXISTS users (
 id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
 email VARCHAR(255) NOT NULL UNIQUE,
 username VARCHAR(255) NOT NULL UNIQUE,
 password VARCHAR(255) NOT NULL,
 verified BOOLEAN NOT NULL DEFAULT FALSE,
 verification_code VARCHAR(255),
 reset_token VARCHAR(255),
 bio TEXT
 )
''')

# Create the categories table if it doesn't exist yet
cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
                   id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                   name VARCHAR(255) NOT NULL UNIQUE,
                   description VARCHAR(255)
               )''')

# Insert some sample categories
categories = [('Checkpoint', 'All types of checkpoint'),
              ('LoRA', 'All types of LoRA'),
              ('Hypernetwork', 'All types of Hypernetwork'),
              ('Textual Inversion', 'All types of Textual Inversion'),
              ('Controlnet', 'All types of Controlnet'),
              ('Image Dataset', 'All types of Image Dataset')]

for category in categories:
    query = "INSERT INTO categories (name, description) SELECT %s, %s WHERE NOT EXISTS (SELECT * FROM categories WHERE name=%s)"
    cursor.execute(query, (*category, category[0]))

# Create the attributes table if it doesn't exist yet
cursor.execute('''CREATE TABLE IF NOT EXISTS attributes (
                   id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                   name VARCHAR(255) NOT NULL UNIQUE,
                   description VARCHAR(255),
                   value_type TEXT
               )''')


# Insert some sample attributes
attributes = [('Training Data', 'The type of training data used'),
              ('Merge', 'Whether the model merges information'),
              ('Model Type', 'The type of model used, e.g. realism, anime, etc.'),
              ('LoRA Type', 'The type of LoRA model used')]

for attribute in attributes:
    query = "INSERT INTO attributes (name, description) SELECT %s, %s WHERE NOT EXISTS (SELECT * FROM attributes WHERE name=%s)"
    cursor.execute(query, (*attribute, attribute[0]))

# Create the category_attributes table if it doesn't exist yet
cursor.execute('''CREATE TABLE IF NOT EXISTS category_attributes (
                   id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                   category_id INT NOT NULL,
                   attribute_id INT NOT NULL,
                   is_required BOOLEAN NOT NULL DEFAULT 0,
                   FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
                   FOREIGN KEY (attribute_id) REFERENCES attributes(id) ON DELETE CASCADE
               )''')



# Create the model_attributes table if it doesn't exist yet
cursor.execute('''CREATE TABLE IF NOT EXISTS model_attributes (
                   id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                   model_id VARCHAR(66) NOT NULL,
                   attribute_id INT NOT NULL,
                   value TEXT,
                   FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
                   FOREIGN KEY (attribute_id) REFERENCES attributes(id) ON DELETE CASCADE
               )''')

# Define the category-attribute relationships
category_attributes = [('Checkpoint', 'Training Data', True),
                       ('Checkpoint', 'Merge', True),
                       ('Checkpoint', 'Model Type', True),
                       ('LoRA', 'LoRA Type', True)]

for category_attribute in category_attributes:
    category_query = "SELECT id FROM categories WHERE name=%s"
    cursor.execute(category_query, (category_attribute[0],))
    category_id = cursor.fetchone()[0]

    attribute_query = "SELECT id FROM attributes WHERE name=%s"
    cursor.execute(attribute_query, (category_attribute[1],))
    attribute_id = cursor.fetchone()[0]

    # Check if the category-attribute relationship already exists
    query = "SELECT * FROM category_attributes WHERE category_id=%s AND attribute_id=%s"
    cursor.execute(query, (category_id, attribute_id))
    if not cursor.fetchone():
        # Insert the category-attribute relationship if it doesn't exist
        query = "INSERT INTO category_attributes (category_id, attribute_id, is_required) VALUES (%s, %s, %s)"
        cursor.execute(query, (category_id, attribute_id, category_attribute[2]))

# Commit the changes and close the database connection
conn.commit()
conn.close()
