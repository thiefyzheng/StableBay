import json
import hashlib

def register(email, username, password):
    # Load the users from the JSON file
    with open('users.json', 'r') as f:
        users = json.load(f)

    # Check if the email already exists
    if any('email' in user and user['email'] == email for user in users.values()):
        return False, 'Email already exists'

    # Check if the username already exists
    if username in users:
        return False, 'Username already exists'

    # Hash the password using sha256
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Add the new user to the dictionary of users
    new_user = {
        'email': email,
        'username': username,
        'password': hashed_password
    }
    users[username] = new_user

    # Write the updated dictionary of users back to the JSON file
    with open('users.json', 'w') as f:
        json.dump(users, f)

    return True, 'Registration successful'
