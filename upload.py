from flask import Flask, render_template, request, redirect, url_for, session
import datetime
import uuid
import mysql.connector

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
    conn.commit()
    if fetchall:
        result = cursor.fetchall()
    else:
        result = cursor.fetchone()
    conn.close()
    return result

# Create models table if it doesn't exist yet
execute_query('''CREATE TABLE IF NOT EXISTS models (
                   id VARCHAR(66) NOT NULL PRIMARY KEY,
                   name VARCHAR(255) NOT NULL,
                   description VARCHAR(255),
                   magnet_link VARCHAR(10000) NOT NULL,
                   image_link VARCHAR(255),
                   uploaded_by VARCHAR(255) NOT NULL,
                   upload_date DATETIME NOT NULL,
                   category INT,
                   nsfw BOOLEAN DEFAULT FALSE
               )''')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('logged_in'):
        # If user is not logged in, redirect to login page
        return redirect(url_for('login'))

    if request.method == 'POST':
        model_name = request.form['model_name']
        short_description = request.form['short_description']
        magnet_link = request.form['magnet_link']
        image_link = request.form['image_link']

        # Generate unique ID
        model_id = str(uuid.uuid4())

        # create dictionary for model info
        model_info = {'id': model_id, 'name': model_name, 'description': short_description, 'magnet_link': magnet_link, 'image_link': image_link,
                      'uploaded_by': session.get('username'), 'upload_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        # Insert model metadata into database
        query = "INSERT INTO models (id, name, description, magnet_link, image_link, uploaded_by, upload_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        params = (model_info['id'], model_info['name'], model_info['description'], model_info['magnet_link'], model_info['image_link'],
                  model_info['uploaded_by'], model_info['upload_date'])
        execute_query(query, params)

        return redirect(url_for('upload2', model_id=model_id))

    return render_template('upload.html')
