import streamlit as st
import pandas as pd
import pyodbc
import time
import os
import io
import sqlalchemy as sa
import zipfile
from win32com.client import Dispatch
import pythoncom  # Add this import

# Initialize the COM library
pythoncom.CoInitialize()
def send_email_with_attachment(file_path):
    outlook = Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.Subject = "Processed Data"
    mail.Body = "Please find attached the processed data file."

    attachment = mail.Attachments.Add(file_path)
    attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "MyAttachment")
    mail.To = "Hanan.akram@ascend.com.sa"  # Replace with recipient's email address
    mail.Send()

    st.text("Email sent successfully!")
# Customizing the layout with CSS
st.markdown(
    """
    <style>
    body {
        background-color: #f0f8ff; /* Light Blue */
    }
    .title {
        color: #336699;
        text-align: center;
        font-size: 2.5em;
        padding: 20px;
    }
    .upload-widget {
        padding: 20px;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
    }
    .button {
        color: white;
        background-color: #336699;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 1.2em;
    }
    .button:hover {
        background-color: #255580;
    }
    .success-text {
        color: #008000;
    }
    .error-text {
        color: #FF0000;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def check_data_quality(df):
    errors = []
    
    null_columns = ['Created At','Region/Cluster','Item Code']
    for col in null_columns:
        if df[col].isnull().any():
            errors.append(f"'{col}' column has null values.")
    
    date_format_errors = []
    if 'Created At' in df.columns:
        try:
            pd.to_datetime(df['Created At'], format='%m/%d/%Y', errors='raise')
        except ValueError:
            date_format_errors.append("Invalid date format in 'Created At' column. Date should be in the format: 3/19/2024")

    return errors, date_format_errors

def process_file(file_path):
    with open(file_path, 'rb') as f:
        io_buffer = io.BytesIO(f.read())
        
    xls = pd.ExcelFile(io_buffer)
    df = pd.read_excel(xls)
    
    null_errors, date_format_errors = check_data_quality(df)

    if null_errors or date_format_errors:
        if null_errors:
            st.error("\n".join(null_errors))
        if date_format_errors:
            st.error("\n".join(date_format_errors))
        return  # Return early if there are any errors
    df.rename(columns={"Region/Cluster": "location", "Item Code": "Generic"},inplace=True)
    df=df[['TicketID','Created At','Generic','location','Status','Type Of Tickets']]
    df['Created At']=df['Created At'].astype(str) 
    df['Generic']=df['Generic'].astype(str) 
    processed_file_path = os.path.join(os.path.dirname(file_path), 'processed_file.csv')
    df.to_csv(processed_file_path, index=False)
    st.text(f"Processed file saved to: {processed_file_path}")

    st.text("Waiting for 20 seconds...")
    time.sleep(20)

    engine =sa.create_engine("mssql+pyodbc://hananrao1:hananrao825825@RAO-HANAN:1433/HR?driver=ODBC Driver 17 for SQL Server") 

    df.to_sql("Ticketing",engine,if_exists='replace',index=False)

    try:
        st.markdown('<p class="success-text">Bulk insert successful.</p>', unsafe_allow_html=True)
        query=("Select *from [HR].[dbo].[Ticketing]")
        data = pd.read_sql(query,engine)
        st.write(data)
    except Exception as e:
        st.error(f"Error during bulk insert: {e}")


    processed_file_path_2 = os.path.join(os.path.dirname(file_path), 'processed_file_2.csv')
    data.to_csv(processed_file_path_2, index=False)
    st.text(f"Processed file saved to: {processed_file_path_2}")
    absolute_file_path = os.path.abspath(file_path)

    # Create a zip file containing processed data
    zip_file_path = os.path.join(os.path.dirname(absolute_file_path), 'processed_data_2.zip')
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        zipf.write(processed_file_path_2, os.path.basename(processed_file_path_2))
        
    # Send email with the zip file attached
    send_email_with_attachment(zip_file_path)


st.markdown('<h1 class="title">Data Processing App</h1>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    if st.button("Check", key='check_button'):
        process_file(uploaded_file.name)