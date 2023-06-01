from flask import Flask, render_template, request, redirect
import re
import psycopg2
from configparser import ConfigParser
import bcrypt

def config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db

params = config()

conn = psycopg2.connect(**params)
print(conn)

cursor = conn.cursor()
print(cursor)

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL NOT NULL PRIMARY KEY, 
        email VARCHAR(255) NOT NULL UNIQUE, 
        username VARCHAR(255) NOT NULL UNIQUE, 
        password VARCHAR(255) NOT NULL
    );
    """)
conn.commit()

app = Flask(__name__)

def is_valid_password(input_str):
    # Check if the input matches the pattern
    pattern = r"^(?=.*[0-9])(?=.*[\W_])(?!.*\s)[A-Za-z0-9\W_]{6,}$"
    return bool(re.match(pattern, input_str))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #check if in database
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s;", (username, password))
        user = cursor.fetchone()
        print(user)
        if user is None:
            return render_template('login.html', invalid=True)
        return 'Got it!' #redirect('/home.html')
    else:
        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        #check if valid according to rules
        #invalid = False
        #exist=False
        if is_valid_password(password):
            try:
                cursor.execute("""
                    INSERT INTO users (email, username, password)
                    VALUES (%s, %s, %s);
                    """, (email, username, password))
                conn.commit()
                return 'You registered succesfully!' #redirect('/home.html')
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                conn.rollback()
                return render_template('signup.html', exist=True)
        else:
            #invalid = True
            return render_template('signup.html', invalid=True)
    else:
        return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)