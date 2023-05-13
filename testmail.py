import yagmail

# Load the password from a text file
with open('password.txt', 'r') as f:
    password = f.read().strip()

# Set up the connection to the Gmail account
yag = yagmail.SMTP('stablebay.org@gmail.com', password)

# Compose the email
to = 'thiefyzheng@gmail.com'
subject = 'Test Email'
body = 'This is a test email sent using yagmail.'

# Send the email
yag.send(to=to, subject=subject, contents=body)
