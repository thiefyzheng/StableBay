import hashlib
import json

from flask import Flask, redirect, url_for, session

from account import get_user_torrents
from authent import register
from torrents import get_torrents
from upload import upload

import database

import mysql.connector
from config import db_password
from admin import is_admin, get_users, edit_user, get_user, remove_model

# Database configuration
db_host = 'localhost'
db_user = 'stablebay'
db_name = 'StableDB'
# Rest of the code for app.py



app = Flask(__name__)
app.secret_key = 'my_secret_key'
database


# Route for the homepage
@app.route('/')
def index():
    # Establish database connection
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

    cursor = conn.cursor()

    # Retrieve category names and ids from the database
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()

    # Retrieve the homepage message from the database
    cursor.execute("SELECT message FROM homepage LIMIT 1")
    row = cursor.fetchone()
    message = row[0] if row else ''

    # Close database connection
    cursor.close()
    conn.close()

    return render_template('index.html', categories=categories, user=session.get('user'), message=message)




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
    page = request.args.get('page', 1, type=int)
    limit = 16
    offset = (page - 1) * limit

    print('Search query:', query)
    print('Category:', category)

    # Open database connection
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()

    # Retrieve category names and ids from the database
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()

    # Calculate the total number of search results
    cursor.execute("SELECT COUNT(*) FROM models WHERE name LIKE %s OR description LIKE %s", ('%' + query + '%', '%' + query + '%'))
    total = cursor.fetchone()[0]

    # Close database connection
    cursor.close()
    conn.close()

    results = search_torrents(query, category, limit=limit, offset=offset)
    results_json = json.loads(results)

    return render_template('search.html', torrents=results_json, categories=categories, page=page, limit=limit, total=total)






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


from torrents import get_torrents
# Database configuration
db_host = 'localhost'
db_user = 'stablebay'
db_name = 'StableDB'


@app.route('/torrents')
def torrents():
    page = request.args.get('page', 1, type=int)
    limit = 16
    offset = (page - 1) * limit
    torrents_json = get_torrents(limit=limit, offset=offset)
    torrents = json.loads(torrents_json)

    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()

    # Retrieve category names and ids from the database
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()

    # Calculate the total number of torrents
    cursor.execute("SELECT COUNT(*) FROM models")
    total = cursor.fetchone()[0]

    # Close database connection
    cursor.close()
    conn.close()

    # Print the values of page, limit, and total for debugging
    print(f'page: {page}')
    print(f'limit: {limit}')
    print(f'total: {total}')

    return render_template('torrents.html', torrents=torrents, categories=categories, page=page, limit=limit,
                           total=total)


from flask import render_template, session
import datetime

import mysql.connector

import edit
from edit import  execute_query, edit_model, update_model_attribute, delete_model_attribute
from flask import redirect, session

from flask import redirect, session, flash

from admin import is_admin
@app.route('/torrents/<string:torrent_id>/edit', methods=['GET', 'POST'])
def edit_torrent(torrent_id):
    if request.method == 'POST':
        # Check if editor is uploader
        editor = session.get('username')
        query = "SELECT uploaded_by FROM models WHERE id=%s"
        params = (torrent_id,)
        uploader = execute_query(query, params)[0]
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

        # Parse updated attribute values from form data
        updated_attributes = {}
        for key, value in request.form.items():
            if key.startswith('update_attribute_'):
                attribute_name = key[len('update_attribute_'):]
                if attribute_name != "Uploaded By":
                    updated_attributes[attribute_name] = value

        print(
            f"Updating torrent {torrent_id} with values: model_name={model_name}, description={description}, magnet_link={magnet_link}, image_link={image_link}, category={category}, attributes={attributes}")

        edit_model(torrent_id, model_name=model_name, short_description=description, magnet_link=magnet_link,
                   image_link=image_link, category=category, attributes=attributes)

        # Update individual attribute values
        #print(f"updated_attributes: {updated_attributes}")
        # for attribute_name, value in updated_attributes.items():
        # update_model_attribute(torrent_id, attribute_name, value)

        return redirect('/updated')  # modified

    else:
        # Check if current user is uploader or admin
        current_user = session.get('username')
        query = "SELECT uploaded_by FROM models WHERE id=%s"
        params = (torrent_id,)
        uploader = execute_query(query, params)[0]
        if current_user != uploader and not is_admin(current_user):
            return redirect('/rickroll')

        # Get torrent details from database
        torrent = get_torrent_details(torrent_id)

        if torrent is None:
            return "Torrent not found"

        # Filter out the Uploaded By attribute
        torrent['attributes'] = [attribute for attribute in torrent['attributes'] if attribute['name'] != 'Uploaded By']

        # Get categories from database
        categories = get_categories()

        # Render edit form
        return render_template('edit_torrent.html', torrent=torrent, categories=categories)





@app.route('/torrents/<string:torrent_id>/edit/delete_all_attributes', methods=['DELETE'])
def delete_all_attributes(torrent_id):
    # Delete all attributes from model_attributes table
    query = "DELETE FROM model_attributes WHERE model_id=%s"
    params = (torrent_id,)
    edit.execute_query(query, params)

    return 'All attributes deleted successfully'


@app.route('/torrents/<string:torrent_id>/edit/delete_attribute/<string:attribute_name>/<string:value>', methods=['DELETE'])
def delete_torrent_attribute(torrent_id, attribute_name, value):
    # Delete the attribute value from the database
    delete_model_attribute(torrent_id, attribute_name, value)
    return 'Attribute value deleted successfully!'


@app.route('/rickroll')
def rickroll():
    return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ", code=302)


@app.route('/account/<username>')
def account(username):
    # Get the user's torrents and bio from the database
    torrents, bio = get_user_torrents(username)

    # Get the current user's username from the session
    current_username = session.get('username')

    # Render the template and pass the torrents, username, bio and current user's username
    return render_template('account.html', torrents=torrents, username=username, bio=bio, current_username=current_username)


from authent import edit_user, get_user_by_username
from flask import session

from flask import session

@app.route('/account/<username>/edit', methods=['GET', 'POST'])
def edit_user_bio(username):
    # Check if the current user is the same as the user being edited
    current_username = session.get('username')
    if current_username != username:
        # Redirect to the /rickroll route
        return redirect(url_for('rickroll'))

    user = get_user_by_username(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    user_id = user['id']
    if request.method == 'GET':
        # Handle GET requests here
        return render_template('edit_bio.html', user=user)
    elif request.method == 'POST':
        # Handle POST requests here
        data = request.form
        if not data:
            return jsonify({'error': 'Missing data'}), 400
        new_bio = data.get('bio')
        edit_user(user_id, new_bio=new_bio)
        return redirect(url_for('account', username=username))



from torrent_details import get_torrent_details

from authent import send_reset_code
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    # Handle form submission
    if request.method == 'POST':
        # Check if the reset_code field is present in the form data
        if 'reset_code' in request.form:
            # Get the reset code and new password from the form data
            reset_code = request.form['reset_code']
            new_password = request.form['new_password']

            # Check if the reset code is valid
            conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
            cursor = conn.cursor()
            query = "SELECT * FROM users WHERE reset_token=%s"
            cursor.execute(query, (reset_code,))
            user = cursor.fetchone()
            if not user:
                flash('Invalid reset code')
                return redirect(url_for('reset_password'))

            # Hash the new password using sha256
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

            # Update the user's password and delete the reset code from the database
            query = "UPDATE users SET password=%s, reset_token=NULL WHERE reset_token=%s"
            cursor.execute(query, (hashed_password, reset_code))

            # Commit the changes and close the database connection
            conn.commit()
            conn.close()

            flash('Password reset successfully')
            return redirect(url_for('login'))
        else:
            # Get the email from the form data
            email = request.form['email']

            # Send the reset code to the user's email
            success, message = send_reset_code(email)
            if not success:
                flash(message)
                return redirect(url_for('reset_password'))

    # Render the reset password form
    return render_template('reset_password.html')




@app.route('/torrents/<string:torrent_id>', methods=['GET'])
def torrent_details(torrent_id):
    # Get the torrent details using the provided ID
    torrent = get_torrent_details(torrent_id)

    # Check if the torrent exists
    if not torrent:
        return "Torrent not found", 404

    # Call the is_admin function with the session['username'] value (if it's set)
    username = session.get('username')
    admin_status = is_admin(username)

    # Render the template with the torrent data and the admin_status value
    return render_template('torrent_details.html', torrent=torrent, is_admin=admin_status)



@app.route('/torrents/<string:torrent_id>/delete', methods=['POST'])
def delete_torrent(torrent_id):
    # Check if the current user is an admin
    if is_admin(session['username']):
        # Call the remove_model function to delete the torrent
        remove_model(torrent_id)
        # Redirect to the home page
        return redirect(url_for('torrents'))
    else:
        # Return an error response if the user is not an admin
        return 'Unauthorized', 401


from comments import add_comment, delete_comment, edit_comment, upvote_comment, downvote_comment, get_comment

@app.route('/torrents/<torrent_id>/comments', methods=['POST'])
def add_torrent_comment(torrent_id):
    # Get the username from the session
    username = session['username']
    # Connect to the database
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()
    # Query the database to get the user's id
    query = "SELECT id FROM users WHERE username=%s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    # Check if a user was found
    if result:
        # Get the user's id
        user_id = result[0]
        # Get the comment from the form data
        comment = request.form['comment']
        # Add the comment to the database
        add_comment(torrent_id, user_id, comment)
        # Redirect to the torrent details page
        return redirect(url_for('torrent_details', torrent_id=torrent_id))
    else:
        # Render an error page or message
        pass


@app.route('/comments/<int:comment_id>/edit', methods=['GET', 'POST'])
def edit_comment_route(comment_id):
    if request.method == 'POST':
        print("Received POST request")
        # Get the new comment text from the form data
        new_comment = request.form.get('comment')
        print(f"Received comment from back end: {new_comment}")
        # Update the comment in the database
        edit_comment(comment_id, new_comment)
        # Return a simple message
        return redirect(url_for('updated'))
    else:
        print("Received GET request")
        # Get the current comment text from the database
        comment = get_comment(comment_id)
        print(f"Current comment text: {comment['comment']}")
        # Render the edit comment form
        return render_template('edit_comment.html', comment=comment)


@app.route('/updated')
def updated():
    return render_template('updated.html')


import os
import json
from flask import jsonify, request
@app.route('/comments/<int:comment_id>/upvote', methods=['POST'])
def upvote(comment_id):
    # Connect to the database
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()

    # Get the current user's username from the session
    username = session.get('username')

    # Get the current user's ID from the database using their username
    query = "SELECT id FROM users WHERE username=%s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    if result:
        user_id = result[0]
        # Call the upvote_comment function
        upvote_comment(user_id, comment_id)
    else:
        print("User not found")

    # Close the database connection
    cursor.close()
    conn.close()

    # Redirect back to the torrent details page
    return redirect(request.referrer)


@app.route('/comments/<int:comment_id>/downvote', methods=['POST'])
def downvote(comment_id):
    # Connect to the database
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()

    # Get the current user's username from the session
    username = session.get('username')

    # Get the current user's ID from the database using their username
    query = "SELECT id FROM users WHERE username=%s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    if result:
        user_id = result[0]
        # Call the downvote_comment function
        downvote_comment(user_id, comment_id)
    else:
        print("User not found")

    # Close the database connection
    cursor.close()
    conn.close()

    # Redirect back to the torrent details page
    return redirect(request.referrer)

from flask import session

@app.route('/comments/<int:comment_id>/delete', methods=['POST', 'DELETE'])
def delete_comment_route(comment_id):
    # Get the username from the session
    username = session.get('username')
    if username:
        if is_admin(username):
            # The user is an admin, proceed with deleting the comment
            delete_comment(comment_id)
            # Redirect to the comments page
            return redirect(url_for('comments'))
        else:
            conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
            cursor = conn.cursor()
            # Check if the username associated with the comment matches the username in the session
            query = "SELECT users.username FROM comments JOIN users ON comments.user_id = users.id WHERE comments.id=%s"
            cursor.execute(query, (comment_id,))
            result = cursor.fetchone()
            if result and result[0] == username:
                # The usernames match, proceed with deleting the comment
                delete_comment(comment_id)
                # Redirect to the comments page
                return redirect(url_for('comments'))
            else:
                # The usernames do not match or the comment does not exist
                flash('Cannot delete comment')
                return redirect(url_for('comments'))
            cursor.close()
            conn.close()
    else:
        # The user is not logged in
        flash('Please log in to delete comments')
        return redirect(url_for('login'))

from flask import render_template
from admin import is_admin

from flask import render_template

import admin

@app.route('/admin')
def admin():
    # Check if the current user is an admin
    if not is_admin(session.get('username')):
        # If the user is not an admin, redirect to the homepage or show an error message
        return redirect(url_for('index'))

    # Retrieve a list of users using the get_users function from admin.py
    users = get_users()

    # Print the list of users
    for user in users:
        print(f"ID: {user[0]}, Email: {user[1]}, Username: {user[2]}")

    # Render the admin page and pass the list of users to the template
    return render_template('admin.html', users=users)


from flask import render_template

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user_page(user_id):
    # Check if user is an admin
    if not is_admin(session.get('username')):
        return jsonify({'error': 'Unauthorized'}), 401

    if request.method == 'GET':
        # Handle GET requests here
        user = get_user(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return render_template('edit_user.html', user=user)
    elif request.method == 'POST':
        # Handle POST requests here
        data = request.form
        if not data:
            return jsonify({'error': 'Missing data'}), 400
        new_verified = data.get('verified') == 'on'
        new_is_admin = int(data.get('is_admin') == 'on')
        edit_user(user_id,
                  new_email=data.get('email'),
                  new_username=data.get('username'),
                  new_password=data.get('password'),
                  new_verified=new_verified,
                  new_verification_code=data.get('verification_code'),
                  new_reset_token=data.get('reset_token'),
                  new_bio=data.get('bio'),
                  new_is_admin=new_is_admin)
        return redirect(url_for('admin'))

@app.route('/admin')
def admin_index():
    # Handle requests to /admin here
    pass

from admin import set_homepage_message
from flask import session, redirect, url_for

@app.route('/admin/message', methods=['GET', 'POST'])
def admin_message():
    if not is_admin(session.get('username')):
        return redirect(url_for('rickroll'))
    if request.method == 'POST':
        message = request.form['message']
        set_homepage_message(message)
        flash('Message updated successfully')
        return redirect(url_for('admin_message'))
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()
    query = "SELECT message FROM homepage LIMIT 1"
    cursor.execute(query)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    message = row[0] if row else ''
    return render_template('admin_message.html', message=message)


@app.route('/admin/message/delete', methods=['POST'])
def delete_homepage_message():
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()
    query = "DELETE FROM homepage"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    flash('Message deleted successfully')
    return redirect(url_for('admin_message'))





import os
from flask import send_from_directory

@app.route('/tos')
def tos():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'tos.txt', as_attachment=False)
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')

import articles

from datetime import datetime
@app.route('/articles')
def show_articles():
    # Get the latest articles from the database
    latest_articles = articles.get_articles()

    # Render the template with the latest articles
    return render_template('articles.html', articles=latest_articles)

@app.route('/articles/create', methods=['GET', 'POST'])
def create_article():
    # Check if the user is an admin
    if not is_admin(session.get('username')):
        # If the user is not an admin, redirect to the /rickroll route
        return redirect('/rickroll')

    if request.method == 'POST':
        # Get the form data
        title = request.form['title']
        text = request.form['text']

        # Set the date to the current date
        date = datetime.now().date()

        # Create the new article
        articles.create_article(title, text)

        # Redirect to the articles page
        return redirect(url_for('show_articles'))
    else:
        # Render the create article form
        return render_template('create_article.html')


from flask import Flask, render_template
import articles
from articles import get_article, edit_article, delete_article


@app.route('/articles/<int:id>')
def show_article(id):
    # Get the article with the specified ID
    article = articles.get_article(id)

    # Render the template with the article data
    return render_template('article.html', article=article)


@app.route('/articles/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    # Check if the user is an admin
    if not is_admin(session.get('username')):
        # If the user is not an admin, redirect to the /rickroll route
        return redirect('/rickroll')

    if request.method == 'POST':
        # Get the updated title and text from the form
        title = request.form['title']
        text = request.form['text']

        # Update the article in the database
        edit_article(id, title, text)

        # Redirect to the article page
        return redirect(url_for('show_article', id=id))
    else:
        # Get the article from the database
        article = get_article(id)

        # Render the edit page
        return render_template('edit_article.html', article=article)


@app.route('/articles/<int:id>/delete', methods=['GET', 'POST'])
def delete(id):
    # Check if the user is an admin
    if not is_admin(session.get('username')):
        # If the user is not an admin, redirect to the /rickroll route
        return redirect('/rickroll')

    if request.method == 'POST':
        # Delete the article from the database
        delete_article(id)

        # Redirect to the articles page
        return redirect(url_for('show_articles'))
    else:
        # Render the delete confirmation page
        return render_template('delete_article.html', id=id)

@app.route('/partners')
def partners():
    return render_template('partners.html')

if __name__ == '__main__':
    print('Running app.py')
    app.run()
