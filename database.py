import mysql.connector

from config import db_password
# Database configuration
db_host = 'localhost'
db_user = 'stablebay'
db_name = 'StableDB'

# Connect to the database
conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

# Create a cursor to execute queries
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS models (
 id VARCHAR(66) NOT NULL PRIMARY KEY,
 name VARCHAR(255) NOT NULL,
 description TEXT,
 magnet_link VARCHAR(10000) NOT NULL,
 image_link VARCHAR(255),
 uploaded_by VARCHAR(255) NOT NULL,
 upload_date DATETIME NOT NULL,
 category INT,
 nsfw BOOLEAN DEFAULT FALSE
 )''')

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
        bio TEXT,
        is_admin BOOLEAN NOT NULL DEFAULT FALSE
    )
''')



# Create the articles table if it doesn't exist yet
cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INT AUTO_INCREMENT PRIMARY KEY,
        writer VARCHAR(255) NOT NULL,
        title VARCHAR(255) NOT NULL,
        text TEXT NOT NULL,
        date DATE NOT NULL
    )
''')






# Create comment_votes table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS comment_votes (
        user_id INT NOT NULL,
        comment_id INT NOT NULL,
        vote TINYINT NOT NULL
    )
''')


# Create the homepage table if it doesn't exist yet
cursor.execute('''
    CREATE TABLE IF NOT EXISTS homepage (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        message TEXT
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
              ('Image Dataset', 'All types of Image Dataset'),
              ('Model Pack', 'All types of Model Pack'),
              ('GitHub Backup', 'All types of GitHub Backup'),
              ('LLM', 'All types of LLM')]

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
              ('LoRA Type', 'The type of LoRA model used'),
              ('Trigger Words', 'The trigger words used by the model'),
              ('File Type', 'The type of file used by the model'),
              ('Quantization', 'The quantization used')]

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

# Define the category-attribute relationships
category_attributes = [('Checkpoint', 'Training Data'),
                       ('Checkpoint', 'Merge'),
                       ('Checkpoint', 'Model Type'),
                       ('LoRA', 'LoRA Type'),
                       ('LoRA', 'Training Data'),
                       ('LoRA', 'Trigger Words'),
                       ('Textual Inversion', 'Training Data'),
                       ('Textual Inversion', 'Trigger Words'),
                       ('Hypernetwork', 'Training Data'),
                       ('Hypernetwork', 'Trigger Words'),
                       ('Controlnet', 'Training Data'),
                       ('LLM', 'Quantization'),
                       ('LLM', 'Training Data'),
                       ('LLM', 'File Type'),
                       ('LLM', 'Merge')]

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
        query = "INSERT INTO category_attributes (category_id, attribute_id) VALUES (%s, %s)"
        cursor.execute(query, (category_id, attribute_id))

# Get the ID of the File Type attribute
attribute_query = "SELECT id FROM attributes WHERE name='File Type'"
cursor.execute(attribute_query)
file_type_attribute_id = cursor.fetchone()[0]

# Link every category with the File Type attribute
category_query = "SELECT id FROM categories"
cursor.execute(category_query)
for category_id in cursor.fetchall():
    query = "INSERT INTO category_attributes (category_id, attribute_id) VALUES (%s, %s)"
    cursor.execute(query, (category_id[0], file_type_attribute_id))

# Commit the changes and close the database connection
conn.commit()
conn.close()

