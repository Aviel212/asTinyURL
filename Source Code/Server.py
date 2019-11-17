import os
import sqlite3
import json
import re
import sys
import datetime
from flask import Flask, request, send_from_directory
from flask_cors import CORS

# creating the app object for Flask
app = Flask(__name__)

# enabling CORS Policies
CORS(app)



# return the appropriate string for the query
def get_time_val(time_re):
    if(time_re == 'min'):
        return '-1 Minute'
    elif(time_re == 'hour'):
        return '-1 Hour'
    elif(time_re == 'day'):
        return '-1 Day'
    else:
        return ''

# Connects to the Db, executes a query and commit the changes
def run_query_and_commit(query):
    try:
        db = sqlite3.connect('./Db/database.db')
        cur = db.cursor()
        cur.execute(query)
        db.commit()
        cur.close()
    except sqlite3.Error as er:
        print("Error while connecting to DB: ", er)
    finally:
        if(db):
            db.close()

# Connects to the Db, executes a query and returns the rows
# from the Db's answer
def run_query_get_rows(query):
    rows = []
    try:
        db = sqlite3.connect('./Db/database.db')
        cur = db.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
    except sqlite3.Error as er:
        print("Error while connecting to DB: ", er)
    finally:
        if(db):
            db.close()
        return rows

# Connects to the Db, executes a query with an object
# and commit the changes
def run_query_obj_and_commit(query, obj):
    try:
        db = sqlite3.connect('./Db/database.db')
        cur = db.cursor()
        cur.execute(query, obj)
        db.commit()
        cur.close()
    except sqlite3.Error as er:
        print("Error while connecting to DB: ", er)
    finally:
        if(db):
            db.close()

# Connects to the Db, executes a query with an object
# and returns the rows from the Db's answer
def run_query_obj_get_rows(query, obj):
    rows = []
    try:
        db = sqlite3.connect('./Db/database.db')
        cur = db.cursor()
        cur.execute(query, obj)
        rows = cur.fetchall()
        cur.close()
    except sqlite3.Error as er:
        print("Error while connecting to DB: ", er)
    finally:
        if(db):
            db.close()
        return rows

# the function runs 3 queries to create the tables in the Db
# if the Db doesn't exist it craetes it
def check_connectivity_db():
    query = '''CREATE TABLE IF NOT EXISTS Short_URLs( 
                key TEXT PRIMARY KEY, 
                long_URL TEXT NOT NULL);'''
    run_query_and_commit(query)
    query = '''CREATE TABLE IF NOT EXISTS Errors(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date timestamp NOT NULL);'''
    run_query_and_commit(query)
    query = '''CREATE TABLE IF NOT EXISTS Redirection(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date timestamp NOT NULL, 
                short_url TEXT,
                FOREIGN KEY(short_url) REFERENCES Short_URLs(key));'''
    run_query_and_commit(query)



# before the app starts running,
# checks that the Db exists and creates it if it doesn't
check_connectivity_db()

# the main page of the server,
# it directs the client to a static file 'index.html'
# which is placed in 'Client' folder
@app.route('/')
def homepage():
    index = 'index.html'
    return send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'), index, mimetype='text/html')

# returns the icon for the Flask App
@app.route('/favicon.ico')
def favicon():
    icon = 'favicon.ico'
    return send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'), icon, mimetype='image/vnd.microsoft.icon')

# the Get Short URL endpoint
# the function gives the new 'long URL' that the client entered
# a new 'short URL' and stores the data in the Db
@app.route('/gsurl/', methods=['POST'])
def get_short_url():
    i = int(get_list_amount())
    key = f'NV{i+1}'
    new_url = f'http://localhost:5000/{key}'
    query = '''INSERT INTO Short_URLs
                   VALUES(?, ?)'''
    new_list = (key, request.get_data())
    run_query_obj_and_commit(query, new_list)
    return new_url

# the stats page for the server,
# it directs the client to a static file 'stats.html'
# which is placed in 'Client' folder
@app.route('/stats')
def statspage():
    stats = 'stats.html'
    return send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'), stats, mimetype='text/html')

# the Errors Amount Endopint,
# it runs a query on the Db that returns the rows in the Errors table
# which were submitted at a time shorter then 1 min, 1 hour or 1 day
# depends on the time the client asks ('min' | 'hour' | 'day').
# the server calculates the number of rows and returns it as a string
@app.route('/amount/errors', methods=['POST'])
def get_errors_amount():
    query = '''SELECT * FROM Errors
                WHERE datetime(date) >= datetime('now', ?, 'localtime');'''
    time = get_time_val(request.get_data().decode('utf-8'))
    return str(len(run_query_obj_get_rows(query, (time, ))))

# the short_URL's Amount Endopint,
# it runs a query on the Db that returns the rows in the Short_URL table
# the server calculates the number of rows and returns it as a string
@app.route('/amount/surl')
def get_list_amount():
    query = '''SELECT * FROM Short_URLs'''
    list_amount = len(run_query_get_rows(query))
    return str(list_amount)


# the Redirections Amount Endopint,
# it runs a query on the Db that returns the rows in the Errors table
# which were submitted at a time shorter then 1 min, 1 hour or 1 day
# depends on the time the client asks ('min' | 'hour' | 'day').
# the server calculates the number of rows and returns it as a string
@app.route('/amount/redirections', methods=['POST'])
def get_redirections_amount():
    query = '''SELECT * FROM Redirection 
                WHERE datetime(date) >= datetime('now', ?, 'localtime');'''
    time = get_time_val(request.get_data().decode('utf-8'))
    return str(len(run_query_obj_get_rows(query, (time, ))))

# the Go To URL Endpoint,
# it runs a query on the Db that returns the row which fits to the index
# which sent, the server takes the Long URL that fits the index sent and
# sends another request to the server to add a line to Redirections table
# it returns a webpage structure that will run the Long URL which was
# recieved from the Db
@app.route('/<string:index>')
def goto_url(index):
    pattern = re.compile("NV[0-9]|NV[1-9][0-9]*")
    lurl = ''
    if(re.match(pattern, index)):
        query = '''SELECT * FROM Short_URLs
                    WHERE key=?'''
        row = run_query_obj_get_rows(query, (index, ))
        lurl = row[0][1].decode('utf-8')
        query = '''INSERT INTO Redirections(date, short_url)
                    VALUES(?, ?)'''
        run_query_obj_and_commit(query, (datetime.datetime.now(), index, ))
    return f''' <script>
                    document.location.href = "{lurl}";
                </script> '''

# the bad request Endpoint,
# The server reaches here if a 404 (Bad Request) Error were thrown.
# It runs a query on the Db to add a new line to the Errors table
# with the corresponding date and time.
# it retruns an Error page to the client that runs for 3 sec and then returns
# to the root page (the index.html file)
@app.errorhandler(404)
def bad_request_error(error):
    print('An Error Has Occoured: ', error)
    query = '''INSERT INTO Errors(date)
                VALUES(?)'''
    run_query_obj_and_commit(query, (datetime.datetime.now(), ))
    return f''' <h1>OOPS! AN ERROR OCCOURED...</h1>
                <script>
                    setTimeout(() => {{
                        document.location.href = "/";
                    }}, 3000);
                </script> '''
