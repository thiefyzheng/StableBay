import hashlib
import json

from flask import Flask, redirect, url_for, session

from account import get_user_torrents
from authent import register
from torrents import get_torrents
from upload import upload
import mysql.connector
# Database configuration
db_host = 'localhost'
db_user = 'stablebay'
db_password = '6969'
db_name = 'StableDB'
# Rest of the code for app.py



app = Flask(__name__)
app.secret_key = 'my_secret_key'

# Load the JSON data
with open('torrents.json', 'r') as f:
    data = json.load(f)

# Route for the homepage
@app.route('/')
def index():
    # Establish database connection
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

    cursor = conn.cursor()

    # Retrieve category names and ids from the database
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()

    # Close database connection
    cursor.close()
    conn.close()

    print(categories)
    return render_template('index.html', categories=categories, user=session.get('user'))



# Route for displaying a single torrent
@app.route('/torrent/<int:id>')
def torrent(id):
    # Find the torrent with the specified ID
    torrent = next((t for t in data['torrents'] if t['id'] == id), None)
    if torrent:
        # Render the template with the torrent data
        return render_template('torrent.html', torrent=torrent, user=session.get('username'))
    else:
        # If the torrent does not exist, redirect to the homepage
        return redirect(url_for('index'))


from search import search_torrents


@app.route('/search')
def search():
    query = request.args.get('query')
    category = request.args.get('category')

    print('Search query:', query)
    print('Category:', category)

    # Open database connection
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()

    # Retrieve category names and ids from the database
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()

    # Close database connection
    cursor.close()
    conn.close()

    results = search_torrents(query, category)
    results_json = json.loads(results)

    return render_template('search.html', torrents=results_json, categories=categories)











from flask import request
from flask import render_template

# Route for the register page
@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        register_result, register_message = register(email, username, password)
        if register_result:
            return redirect(url_for('verify_route'))
        else:
            return render_template('register.html', error=register_message)
    else:
        return render_template('register.html')

from verify import verify

from authent import resend_verification_code
import yagmail
@app.route('/verify', methods=['GET', 'POST'])
def verify_route():
    # Get the verification code from the URL or form data
    verification_code = request.args.get('code') or request.form.get('verification_code')

    if request.method == 'POST' and request.form.get('resend_code'):
        # Resend verification code
        # Connect to the database
        conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

        # Create a cursor to execute queries
        cursor = conn.cursor()

        # Get the user's email from the database
        query = "SELECT email FROM users WHERE username=%s"
        cursor.execute(query, (session['username'],))
        result = cursor.fetchone()
        if result:
            email = result[0]

            # Call the resend_verification_code function
            resend_verification_code(email)

        # Close the database connection
        conn.close()

        return render_template('verify.html', resend_success="Verification code resent")
    elif verification_code:
        # Verify the email using the verify function from verify.py
        verify_result, verify_message = verify(verification_code)
        if verify_result:
            # Render the verify page with a success message
            return render_template('verify.html', success=verify_message)
        else:
            # Render the verify page with an error message
            return render_template('verify.html', error=verify_message)
    else:
        # Render the verify page
        return render_template('verify.html')


# Route for the login page
# Database configuration
db_host = 'localhost'
db_user = 'stablebay'
db_password = '6969'
db_name = 'StableDB'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the submitted credentials
        username = request.form['username']
        password = request.form['password']

        # Connect to the database
        conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

        # Create a cursor to execute queries
        cursor = conn.cursor()

        # Check if the user exists and the password is correct
        query = "SELECT * FROM users WHERE username=%s AND password=%s"
        cursor.execute(query, (username, hashlib.sha256(password.encode()).hexdigest()))
        result = cursor.fetchone()
        print(f'Query result: {result}')
        if result:
            # Set the user as logged in
            session['logged_in'] = True
            session['username'] = username
            # Print a message to the console
            print(f'{username} has logged in')
            # Redirect to the homepage
            return redirect(url_for('index'))
        else:
            # Render the login page with an error message
            return render_template('login.html', error='Invalid username or password')
    else:
        # Render the login page
        return render_template('login.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_route():
    if request.method == 'POST':
        result = upload()

        return result

    return render_template('upload.html')


from upload2 import get_categories, get_attributes, add_model_attributes
import mysql.connector
db_host = 'localhost'
db_user = 'stablebay'
db_password = '6969'
db_name = 'StableDB'

@app.route('/upload2/<string:model_id>', methods=['GET', 'POST'])
def upload2(model_id):
    if not session.get('logged_in'):
        # If user is not logged in, redirect to login page
        return redirect(url_for('login'))

    categories = get_categories() # get the list of categories
    print("Categories:", categories)

    category_attributes = [] # initialize category_attributes to an empty list

    if request.method == 'POST' and request.form.get('request_type') == 'POST':
        category_id = request.form['category_id']
        print("Selected category ID:", category_id)
        print("Form data:", request.form)

        # Get the category attributes for the selected category
        category_attributes = get_attributes(category_id)
        print("Category attributes:", category_attributes)

        # Format the form data
        attribute_values = {}
        for key in request.form.keys():
            if key not in ['category_id', 'request_type']:
                attribute_values[key] = request.form.getlist(key)

        # Convert attribute values to JSON
        attribute_values_json = json.dumps(attribute_values)
        print(f"attribute_values_json: {attribute_values_json}")

        # Save the model attributes to the database
        add_model_attributes(model_id, attribute_values_json)

        # Update the category for the model in the database
        conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = conn.cursor()
        query = '''
        UPDATE models
        SET category = %s
        WHERE id = %s
        '''
        cursor.execute(query, (category_id, model_id))
        conn.commit()
        conn.close()

        # Redirect to the next step in the upload process, passing the model_id as a parameter
        return redirect(url_for('uploaded_route', model_id=model_id))

    return render_template('upload2.html', model_id=model_id, categories=categories, category_attributes=category_attributes)

@app.route('/add_model_attributes/<int:model_id>', methods=['POST'])
def add_model_attributes_endpoint(model_id):
    attribute_values_json = request.form.get('attribute_values')
    add_model_attributes(model_id, attribute_values_json)
    return 'Attributes added to the database.'

@app.route('/get_attributes/<category_id>', methods=['GET'])
def get_attributes_route(category_id):
    try:
        attributes = get_attributes(category_id)
        return jsonify(attributes)
    except:
        return 'Failed to get category attributes', 500


# Route for logging out
@app.route('/logout')
def logout():
    # Clear the session and redirect to the homepage
    session.clear()
    return redirect(url_for('index'))

@app.route('/uploaded')
def uploaded_route():
    return render_template('uploaded.html')


import requests

@app.route('/torrents')
def torrents():

    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()

    # Retrieve category names and ids from the database
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()

    # Close database connection
    cursor.close()
    conn.close()

    torrents_json = get_torrents()
    torrents = json.loads(torrents_json)
    return render_template('torrents.html', torrents=torrents, categories=categories)
from flask import render_template, session
import datetime

import mysql.connector

import edit
from flask import redirect, session

from flask import redirect, session

from admin import is_admin
@app.route('/torrents/<string:torrent_id>/edit', methods=['GET', 'POST'])
def edit_torrent(torrent_id):
    if request.method == 'POST':
        # Check if editor is uploader
        editor = session.get('username')
        query = "SELECT uploaded_by FROM models WHERE id=%s"
        params = (torrent_id,)
        uploader = edit.execute_query(query, params)[0]
        if editor != uploader:
            return redirect('/rickroll')

        model_name = request.form.get('model_name')
        description = request.form.get('description')
        magnet_link = request.form.get('magnet_link')
        image_link = request.form.get('image_link')
        category = request.form.get('category')

        # Parse attributes from form data
        attributes = {}
        for key, value in request.form.items():
            if key.startswith('attribute_'):
                attribute_name = key[len('attribute_'):]
                attributes[attribute_name] = value

        print(
            f"Updating torrent {torrent_id} with values: model_name={model_name}, description={description}, magnet_link={magnet_link}, image_link={image_link}, category={category}, attributes={attributes}")

        edit.edit_model(torrent_id, model_name=model_name, short_description=description, magnet_link=magnet_link,
                        image_link=image_link, category=category, attributes=attributes)

        return 'Torrent updated successfully!'

    else:
        # Check if current user is uploader or admin
        current_user = session.get('username')
        query = "SELECT uploaded_by FROM models WHERE id=%s"
        params = (torrent_id,)
        uploader = edit.execute_query(query, params)[0]
        if current_user != uploader and not is_admin(current_user):
            return redirect('/rickroll')

        # Get torrent details from database
        torrent = get_torrent_details(torrent_id)

        if torrent is None:
            return "Torrent not found"

        # Get categories from database
        categories = edit.get_categories()

        # Render edit form
        return render_template('edit_torrent.html', torrent=torrent, categories=categories)


@app.route('/torrents/<string:torrent_id>/edit/delete_attribute', methods=['DELETE'])
def delete_attribute(torrent_id):
    # Get attribute name from DELETE data
    attribute_name = request.form.get('attribute_name')

    # Get attribute ID from database
    query = "SELECT id FROM attributes WHERE name=%s"
    params = (attribute_name,)
    row = edit.execute_query(query, params)
    if row is None:
        return 'Attribute not found', 404
    attribute_id = row[0]

    # Delete attribute from model_attributes table
    query = "DELETE FROM model_attributes WHERE model_id=%s AND attribute_id=%s"
    params = (torrent_id, attribute_id)
    edit.execute_query(query, params)

    return 'Attribute deleted successfully'

@app.route('/rickroll')
def rickroll():
    return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ", code=302)


@app.route('/account/<username>')
def account(username):
    # Get the user's torrents from the database
    torrents = get_user_torrents(username)

    # Render the template and pass the torrents and username
    return render_template('account.html', torrents=torrents, username=username)

from torrent_details import get_torrent_details


@app.route('/torrents/<string:torrent_id>', methods=['GET'])
def torrent_details(torrent_id):
    # Get the torrent details using the provided ID
    torrent = get_torrent_details(torrent_id)

    # Check if the torrent exists
    if not torrent:
        return "Torrent not found", 404

    # Print the torrent data
    print(torrent)

    # Render the template with the torrent data
    return render_template('torrent_details.html', torrent=torrent)


@app.route('/torrents/<string:torrent_name>/comments/<int:comment_id>', methods=['DELETE','POST'])
def delete_comment(torrent_name, comment_id):
    # Construct path to comments JSON file for the given torrent
    comments_path = os.path.join(app.config['UPLOAD_FOLDER'], torrent_name, 'comments.json')

    # Check if the comments JSON file exists for the given torrent
    if not os.path.exists(comments_path):
        return 'Comments not found', 404

    # Load comments from comments JSON file
    with open(comments_path, 'r') as f:
        comments_data = json.load(f)

    # Find the comment with the given ID
    comment_index = None
    for i, comment in enumerate(comments_data['comments']):
        if comment['id'] == comment_id:
            comment_index = i
            break

    # If the comment doesn't exist, return a 404 error
    if comment_index is None:
        return 'Comment not found', 404

    # Check if the user is authorized to delete the comment
    if 'username' not in session or comments_data['comments'][comment_index]['username'] != session['username']:
        return 'You are not authorized to delete this comment', 401

    # Remove the comment from the comments data
    del comments_data['comments'][comment_index]

    # Write the updated comments data to the comments JSON file
    with open(comments_path, 'w') as f:
        json.dump(comments_data, f)
    return '', 204

import os
import json
from flask import jsonify, request

@app.route('/torrents/<string:torrent_name>/comments/<int:comment_id>/upvote', methods=['POST'])
def upvote_comment(torrent_name, comment_id):
    # Construct path to comments JSON file for the given torrent
    comments_path = os.path.join(app.config['UPLOAD_FOLDER'], torrent_name, 'comments.json')

    # Check if the comments JSON file exists for the given torrent
    if not os.path.exists(comments_path):
        return jsonify({'error': 'Comments not found'}), 404

    # Load comments from comments JSON file
    with open(comments_path, 'r') as f:
        comments_data = json.load(f)

    # Find the comment with the given ID
    comment_index = None
    for i, comment in enumerate(comments_data['comments']):
        if comment['id'] == comment_id:
            comment_index = i
            break

    # If the comment doesn't exist, return a 404 error
    if comment_index is None:
        return jsonify({'error': 'Comment not found'}), 404

    # Update the upvote value of the comment
    comments_data['comments'][comment_index]['upvotes'] += 1

    # Write the updated comments data to the comments JSON file
    with open(comments_path, 'w') as f:
        json.dump(comments_data, f)

    # Return the updated comment data as a JSON response
    return jsonify(comments_data['comments'][comment_index]), 200




@app.route('/torrents/<string:torrent_name>/comments/<int:comment_id>/downvote', methods=['POST'])
def downvote_comment(torrent_name, comment_id):
    # Construct path to comments JSON file for the given torrent
    comments_path = os.path.join(app.config['UPLOAD_FOLDER'], torrent_name, 'comments.json')

    # Check if the comments JSON file exists for the given torrent
    if not os.path.exists(comments_path):
        return 'Comments not found', 404

    # Load comments from comments JSON file
    with open(comments_path, 'r') as f:
        comments_data = json.load(f)

    # Find the comment with the given ID
    comment_index = None
    for i, comment in enumerate(comments_data['comments']):
        if comment['id'] == comment_id:
            comment_index = i
            break

    # If the comment doesn't exist, return a 404 error
    if comment_index is None:
        return 'Comment not found', 404

    # Update the downvote value of the comment
    comments_data['comments'][comment_index]['downvotes'] += 1

    # Write the updated comments data to the comments JSON file
    with open(comments_path, 'w') as f:
        json.dump(comments_data, f)

    return jsonify({'upvotes': comments_data['comments'][comment_index]['upvotes'], 'downvotes': comments_data['comments'][comment_index]['downvotes']})


if __name__ == '__main__':
    print('Running app.py')
    app.run()
