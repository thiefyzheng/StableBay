import hashlib
import json

import os
from torrents import get_torrents

from flask import Flask, render_template, request, redirect, url_for, session

from authent import register
from upload import upload

from account import get_user_torrents



# Rest of the code for app.py



app = Flask(__name__)
app.secret_key = 'my_secret_key'

# Load the JSON data
with open('torrents.json', 'r') as f:
    data = json.load(f)

# Route for the homepage
@app.route('/')
def index():
    torrents = []
    for filename in os.listdir('/home/stablebay/uploads/'):
        if filename.endswith('.torrent'):
            filepath = os.path.join('stablebay/uploads', filename)
            torrent = Torrent.from_file(filepath)
            torrents.append(torrent)
    return render_template('index.html', torrents=torrents, user=session.get('user'))

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

# Route for the register page
@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        register_result, register_message = register(email, username, password)
        if register_result:
            return redirect(url_for('index'))
        else:
            return render_template('register.html', error=register_message)
    else:
        return render_template('register.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the submitted credentials
        username = request.form['username']
        password = request.form['password']

        # Load the users from the JSON file
        with open('users.json', 'r') as f:
            users = json.load(f)

        # Check if the user exists and the password is correct
        if username in users and users[username]['password'] == hashlib.sha256(password.encode()).hexdigest():
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


# Route for logging out
@app.route('/logout')
def logout():
    # Clear the session and redirect to the homepage
    session.clear()
    return redirect(url_for('index'))

@app.route('/uploaded')
def uploaded_route():
    return render_template('uploaded.html')

@app.route('/torrents')
def torrents():
    torrents = get_torrents()
    return render_template('torrents.html', torrents=torrents)


from flask import render_template, session
import os

@app.route('/torrents/<string:torrent_name>/edit', methods=['GET', 'POST'])
def edit_torrent(torrent_name):
    # Construct the path to the info.json file for the given torrent
    info_path = os.path.join(app.config['UPLOAD_FOLDER'], torrent_name, 'info.json')

    # Check if the info.json file exists for the given torrent
    if not os.path.exists(info_path):
        return 'Torrent not found', 404

    # Read the data from the info.json file
    with open(info_path, 'r') as f:
        torrent_data = json.load(f)

    # Check if the current user is the uploader of the torrent
    if 'username' in session and session['username'] == torrent_data['uploaded_by']:
        if request.method == 'POST':
            # Save the edited data to the info.json file
            torrent_data['name'] = request.form['name']
            torrent_data['category'] = request.form['category']
            torrent_data['description'] = request.form['description']

            with open(info_path, 'w') as f:
                json.dump(torrent_data, f, indent=4)

            return redirect(url_for('torrent_details', torrent_name=torrent_name))
        else:
            # Render the edit torrent template with the torrent data
            return render_template('edit_torrent.html', torrent=torrent_data)
    else:
        # Redirect to a "Access Denied" or "Rick Roll" page
        return redirect('/rickroll')


@app.route('/rickroll')
def rickroll():
    return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ", code=302)


@app.route('/torrents/<string:torrent_name>')
def torrent_details(torrent_name):
    # Construct the path to the info.json file for the given torrent
    info_path = os.path.join(app.config['UPLOAD_FOLDER'], torrent_name, 'info.json')

    # Check if the info.json file exists for the given torrent
    if not os.path.exists(info_path):
        return 'Torrent not found', 404

    # Read the data from the info.json file
    with open(info_path, 'r') as f:
        torrent_data = json.load(f)

    # Get the tags from the info.json file
    tags = torrent_data.get('tags', [])

    # Render the template with the torrent data and tags
    return render_template('torrent_details.html', torrent=torrent_data, tags=tags)

@app.route('/account/<username>')
def account(username):
    user_torrents = get_user_torrents(username)
    return render_template('account.html', torrents=user_torrents)



app.config['UPLOAD_FOLDER'] = '/home/stablebay/PycharmProjects/StableBay/uploads'



if __name__ == '__main__':
    print('Running app.py')
    app.run()
