import mysql.connector
from config import db_password
# Database configuration
db_host = 'localhost'
db_user = 'stablebay'

db_name = 'StableDB'

def verify(verification_code):
    # Connect to the database
    conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

    # Create a cursor to execute queries
    cursor = conn.cursor()

    # Check if the verification code is valid
    query = "SELECT * FROM users WHERE verification_code=%s"
    cursor.execute(query, (verification_code,))
    user = cursor.fetchone()
    if not user:
        return False, 'Invalid verification code'

    # Update the verified column to True
    query = "UPDATE users SET verified=TRUE WHERE verification_code=%s"
    cursor.execute(query, (verification_code,))

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()

    return True, 'Email verified successfully'

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print('Usage: python verify.py <verification_code>')
        sys.exit(1)

    verification_code = sys.argv[1]
    success, message = verify(verification_code)
    print(message)
