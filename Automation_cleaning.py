import streamlit as st
import pandas as pd
import pyodbc
import time
import os
import io

def process_file(file_path):
    with open(file_path, 'rb') as f:
        io_buffer = io.BytesIO(f.read())
        
    xls = pd.ExcelFile(io_buffer)
    df = pd.read_excel(xls)
    df.dropna(inplace=True)
    def check_data_quality(df):
        errors = []
        null_columns = list(df.columns)

        for col in null_columns:
            if df[col].isnull().any():
                errors.append(f"{col} column has null values. Error.")
 

        date_format_errors = []
        date_formats_to_try = ['%y-%d-%m', '%Y-%d-%m', '%d-%m-%y', '%d-%m-%Y']  
        for date_format in date_formats_to_try:
            try:
                df['Created_At'] = pd.to_datetime(df['Created_At'], format=date_format, errors='raise')
                df['Created_At'] = pd.to_datetime(df['Created_At'])  # Convert to datetime again
                break  # If successfully converted, break the loop
            except ValueError:
                pass

        return errors, date_format_errors

    null_errors, date_format_errors = check_data_quality(df)

    if null_errors:
        st.error("\n".join(null_errors))
        return  # Return early if there are null errors

    if date_format_errors:
        st.error("\n".join(date_format_errors))
        return  # Return early if there are date format errors

    processed_file_path = os.path.join(os.path.dirname(file_path), 'processed_file.csv') # save processed file 
    df.to_csv(processed_file_path, index=False)
    st.text(f"Processed file saved to: {processed_file_path}")

    st.text("Waiting for 20 seconds...")#-----> Wait for 10 seconds
    time.sleep(10)

    connection_string = f"Driver={{ODBC Driver 17 for SQL Server}};Server={{RAO-HANAN}};Database={{HR}};UID={{hananrao1}};PWD={{hananrao825825}};port={1433}"
    conn = pyodbc.connect(connection_string) #----> make connetion with database
    cursor = conn.cursor()

    # Use parameterized query to prevent SQL injection
    query = (
        "TRUNCATE TABLE Ticketing;"
        "BULK INSERT Ticketing "
        "FROM 'E:\Automation\processed_file.csv' "
        "WITH (FIELDTERMINATOR = ',', ROWTERMINATOR = '\n', FIRSTROW = 2, DATAFILETYPE = 'widechar', CODEPAGE = 'ACP')"
    ) #---->use above query to enter large data using "BULK INSERT" 
    try:
        cursor.execute(query)
        conn.commit()
        st.success("Bulk insert successful.")

        query=("Select * from HR.[dbo].Ticketing")
        data = pd.read_sql(query, conn)
        st.write(data)
    except Exception as e:
        st.error(f"Error during bulk insert: {e}")
    finally:
        cursor.close()
        conn.close()

st.title("Data Processing App")

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    if st.button("Check"):
        process_file(uploaded_file.name)
