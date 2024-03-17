import streamlit as st
import pandas as pd
import pyodbc

# Function to connect to SQL Server and fetch database names
def get_database_names(server, username, password):
    try:
        connection_string = f"Driver={{ODBC Driver 17 for SQL Server}};Server={server};UID={username};PWD={password};port={1433}"
        conn = pyodbc.connect(connection_string)
        query = "SELECT name FROM sys.databases WHERE database_id > 4;"
        databases = [row.name for row in conn.cursor().execute(query)]
        conn.close()
        return databases
    except Exception as e:
        st.error(f"Error connecting to SQL Server: {e}")
        return []

# Function to connect to SQL Server and fetch table names for a given database
def get_table_names(server, database, username, password):
    try:
        connection_string = f"Driver={{ODBC Driver 17 for SQL Server}};Server={server};Database={database};UID={username};PWD={password};port={1433}"
        conn = pyodbc.connect(connection_string)
        query = "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE';"
        tables = [row.table_name for row in conn.cursor().execute(query)]
        conn.close()
        return tables
    except Exception as e:
        st.error(f"Error connecting to SQL Server: {e}")
        return []

# Function to connect to SQL Server and fetch data
def fetch_data(server, database, table, username, password):
    try:
        connection_string = f"Driver={{ODBC Driver 17 for SQL Server}};Server={server};Database={database};UID={username};PWD={password};port={1433}"
        conn = pyodbc.connect(connection_string)
        query = f"SELECT * FROM {table};"
        data = pd.read_sql(query, conn)
        conn.close()
        return data
    except Exception as e:
        st.error(f"Error connecting to SQL Server: {e}")
        return pd.DataFrame()

# Streamlit App
def main():
    st.title("SQL Server Data Fetcher")

    # Sidebar for server, database, and table selection
    server = st.text_input("Enter SQL Server address:")
    username = st.text_input("Enter SQL Server username:")
    password = st.text_input("Enter SQL Server password:", type="password")

    databases = get_database_names(server, username, password)
    
    database = st.sidebar.selectbox("Select Database:", databases) if databases else None

    if database:
        tables = get_table_names(server, database, username, password)
        table = st.sidebar.selectbox("Select Table:", tables) if tables else None

        if table and st.button("Fetch Data"):
            st.write(f"Fetching data from {database}.{table}...")

            # Fetch data
            data = fetch_data(server, database, table, username, password)

            # Display the data
            st.dataframe(data)

if __name__ == "__main__":
    main()
