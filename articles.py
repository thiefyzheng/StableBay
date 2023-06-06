from flask import session
import mysql.connector
from config import db_password

# Database configuration
db_host = 'localhost'
db_user = 'stablebay'
db_name = 'StableDB'

def get_articles():
    # Establish database connection
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()

    # Retrieve articles from the database
    cursor.execute("SELECT id, writer, text, date FROM articles")
    articles = cursor.fetchall()

    # Close database connection
    cursor.close()
    conn.close()

    return articles

def get_article(id):
    # Establish database connection
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()

    # Retrieve the article with the specified ID from the database
    cursor.execute("SELECT id, writer, text, date FROM articles WHERE id=%s", (id,))
    article = cursor.fetchone()

    # Close database connection
    cursor.close()
    conn.close()

    return article

def create_article(text, date):
    # Get the writer from the session data
    writer = session.get('username')

    # Establish database connection
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()

    # Insert the new article into the database
    cursor.execute("INSERT INTO articles (writer, text, date) VALUES (%s, %s, %s)", (writer, text, date))
    conn.commit()

    # Close database connection
    cursor.close()
    conn.close()

def edit_article(id, text):
    # Establish database connection
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()

    # Update the article in the database
    cursor.execute("UPDATE articles SET text=%s WHERE id=%s", (text,id))
    conn.commit()

    # Close database connection
    cursor.close()
    conn.close()

def delete_article(id):
    # Establish database connection
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()

    # Delete the article from the database
    cursor.execute("DELETE FROM articles WHERE id=%s", (id,))
    conn.commit()

    # Close database connection
    cursor.close()
    conn.close()
