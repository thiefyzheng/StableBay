from flask import Flask, render_template, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
import json
import datetime

app = Flask(__name__)



# List of allowed tags
allowed_tags = ['checkpoint', 'lora', 'textual-inversion']


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('logged_in'):
        # If user is not logged in, redirect to login page
        return redirect(url_for('login'))
    if request.method == 'POST':
        model_name = request.form['model_name']
        short_description = request.form['short_description']
        torrent_file = request.files['torrent_file']
        tags = request.form.getlist('tags')

        if torrent_file.filename == '':
            error = 'No file selected'
            return render_template('upload.html', error=error)

        # Check if all provided tags are allowed
        for tag in tags:
            if tag not in allowed_tags:
                error = f'Tag "{tag}" is not allowed'
                return render_template('upload.html', error=error)

        filename = secure_filename(torrent_file.filename)
        file_path = os.path.join('/home/stablebay/uploads', model_name, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        torrent_file.save(file_path)

        # create dictionary for model info and save as JSON file
        model_info = {'name': model_name, 'description': short_description, 'file_path': file_path, 'tags': tags,
                      'uploaded_by': session.get('username'), 'upload_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        json_path = os.path.join('/home/stablebay/PycharmProjects/StableBay/uploads', model_name, 'info.json')
        with open(json_path, 'w') as f:
            json.dump(model_info, f)

        return redirect(url_for('uploaded_route'))

    return render_template('upload.html')
