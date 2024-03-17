import streamlit as st
import pandas as pd
from datetime import datetime

# Sample DataFrame for demonstration
data = {
    'name': ['John', 'Alice', 'Bob'],
    'age': [25, None, 30],
    'date': ['1/15/2022', '12/05/2023', 'invalid_date'],
}

df = pd.DataFrame(data)

# Function to check null values in specified columns and validate date format
def check_data_quality(df):
    errors = []

    # Check for null values in specified columns
    null_columns = ['name', 'age', 'date']
    for col in null_columns:
        if df[col].isnull().any():
            errors.append(f"{col} column has null values. Error.")

    # Validate date format in the 'date' column
    date_format_errors = []
    date_column = 'date'
    for date_str in df[date_column]:
        try:
            datetime.strptime(date_str, '%m/%d/%Y')
        except ValueError:
            date_format_errors.append(f"Invalid date format in {date_column} column. Error.")

    return errors, date_format_errors

# Streamlit app
st.title("Data Quality Check")

# Display the original DataFrame
st.subheader("Original DataFrame:")
st.dataframe(df)

# Check data quality
null_errors, date_format_errors = check_data_quality(df)

# Display errors, if any
if null_errors:
    st.error("\n".join(null_errors))

if date_format_errors:
    st.error("\n".join(date_format_errors))
