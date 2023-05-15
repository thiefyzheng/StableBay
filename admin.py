import edit

def is_admin(username):
    # Check if user is in admin database table
    query = "SELECT is_admin FROM users WHERE username=%s"
    params = (username,)
    result = edit.execute_query(query, params)
    return result is not None and result[0]['is_admin']
