@app.route('/torrents/<string:torrent_name>', methods=['GET', 'POST'])
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

    # Handle comment form submission
    if request.method == 'POST':
        if 'username' not in session:
            return 'You must be logged in to submit a comment', 401

        comment = request.form['comment']
        username = session['username']
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Construct path to comments JSON file for the given torrent
        comments_path = os.path.join(app.config['UPLOAD_FOLDER'], torrent_name, 'comments.json')

        # Load existing comments from comments JSON file (if it exists)
        if os.path.exists(comments_path):
            with open(comments_path, 'r') as f:
                comments_data = json.load(f)
        else:
            comments_data = {'comments': []}

        # Generate a unique ID for the new comment
        comment_id = len(comments_data['comments']) + 1

        # Add the new comment to the comments data with the generated ID
        comments_data['comments'].append({
            'id': comment_id,
            'username': username,
            'timestamp': timestamp,
            'comment': comment,
            'upvotes': 0,
            'downvotes': 0
        })

        # Write the updated comments data to the comments JSON file
        with open(comments_path, 'w') as f:
            json.dump(comments_data, f)

        # Reload the page to display the new comment
        return redirect(request.url)

    # Load comments from comments JSON file (if it exists)
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], torrent_name, 'comments.json')):
        with open(os.path.join(app.config['UPLOAD_FOLDER'], torrent_name, 'comments.json'), 'r') as f:
            comments_data = json.load(f)
            comments = comments_data['comments']
    else:
        comments = []

    # Render the template with the torrent data, tags, and comments
    return render_template('torrent_details.html', torrent=torrent_data, tags=tags, comments=comments)

