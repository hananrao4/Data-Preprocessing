from flask import Flask, render_template, request
import pandas as pd
import pyodbc

app = Flask(__name__, template_folder='templates')

def get_database_names(server, username, password):
    try:
        connection_string = f"Driver={{ODBC Driver 17 for SQL Server}};Server={server};UID={username};PWD={password};Connection Timeout=30;"
        conn = pyodbc.connect(connection_string)
        query = "SELECT name FROM sys.databases WHERE database_id > 4;"
        databases = [row.name for row in conn.cursor().execute(query)]
        conn.close()
        return databases
    except Exception as e:
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    server = request.form['server']
    username = request.form['username']
    password = request.form['password']
    database = request.form['database']

    databases = get_database_names(server, username, password)

    return render_template('result.html', databases=databases)

if __name__ == '__main__':
    app.run(debug=True)
