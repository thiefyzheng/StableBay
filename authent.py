import yagmail
import os
import random
import string
import mysql.connector
import hashlib
from config import db_password
# Database configuration
db_host = 'localhost'
db_user = 'stablebay'

db_name = 'StableDB'

def register(email, username, password):
    # Load the Gmail password from a text file
    with open('password.txt', 'r') as f:
        gmail_password = f.read().strip()

    # Connect to the database
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

    # Create a cursor to execute queries
    cursor = conn.cursor()

    # Check if the email already exists
    query = "SELECT * FROM users WHERE email=%s"
    cursor.execute(query, (email,))
    if cursor.fetchone():
        return False, 'Email already exists'

    # Check if the username already exists
    query = "SELECT * FROM users WHERE username=%s"
    cursor.execute(query, (username,))
    if cursor.fetchone():
        return False, 'Username already exists'

    # Hash the password using sha256
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Generate a random verification code
    verification_code = ''.join(random.choices(string.ascii_letters + string.digits, k=20))

    # Add the new user to the users table
    query = "INSERT INTO users (email, username, password, verification_code) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (email, username, hashed_password, verification_code))

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()

    # Send verification email using yagmail
    yag = yagmail.SMTP('stablebay.org@gmail.com', gmail_password)
    subject = 'Email Verification'
    body = f'Please verify your email by clicking on this link: https://stablebay.org/verify?code={verification_code} or entering this code: {verification_code}'
    yag.send(email, subject, body)

    return True, 'Registration successful'

def resend_verification_code(email):
    # Connect to the database
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

    # Create a cursor to execute queries
    cursor = conn.cursor()

    # Generate a new random verification code
    verification_code = ''.join(random.choices(string.ascii_letters + string.digits, k=20))

    # Update the verification code in the users table
    query = "UPDATE users SET verification_code=%s WHERE email=%s"
    cursor.execute(query, (verification_code, email))

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()

    # Send verification email using yagmail
    with open('password.txt', 'r') as f:
        gmail_password = f.read().strip()
    yag = yagmail.SMTP('stablebay.org@gmail.com', gmail_password)
    subject = 'Email Verification'
    body = f'Please verify your email by clicking on this link: https://stablebay.org/verify?code={verification_code} or entering this code: {verification_code}'
    yag.send(email, subject, body)



def get_user_by_username(username):
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username=%s"
    cursor.execute(query, (username,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        columns = [column[0] for column in cursor.description]
        user = dict(zip(columns, row))
        return user
    else:
        return None













def send_reset_code(email):
    # Connect to the database
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

    # Create a cursor to execute queries
    cursor = conn.cursor()

    # Check if the email is valid
    query = "SELECT * FROM users WHERE email=%s"
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    if not user:
        return False, 'Invalid email'

    # Generate a reset code
    reset_code = ''.join(random.choices(string.ascii_letters + string.digits, k=20))

    # Update the reset_token column with the reset code
    query = "UPDATE users SET reset_token=%s WHERE email=%s"
    cursor.execute(query, (reset_code, email))

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()

    # Send the reset code to the user's email using yagmail
    with open('password.txt', 'r') as f:
        gmail_password = f.read().strip()
    yag = yagmail.SMTP('stablebay.org@gmail.com', gmail_password)
    subject = 'Password Reset'
    body = f'Here is your password reset code: {reset_code}\n\nPlease use this code to reset your password.'
    yag.send(email, subject, body)

    return True, 'Reset code sent successfully'


def edit_user(user_id, new_email=None, new_username=None, new_password=None, new_verified=None, new_verification_code=None, new_reset_token=None, new_bio=None, new_is_admin=None):
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()
    if new_bio:
        query = "UPDATE users SET bio=%s WHERE id=%s"
        cursor.execute(query, (new_bio, user_id))
    conn.commit()
    cursor.close()
    conn.close()




