import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read database connection parameters from environment variables
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv('POSTGRES_PORT')
db_database = os.getenv('POSTGRES_DB')

# Create a database engine
engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}")

st.title("Upload and Save Data to PostgreSQL")

# File upload
uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=['xlsx', 'csv'])
if uploaded_file is not None:
    # Load data into a DataFrame
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)
    
    # Display the data in a table
    st.write("Data Preview:")
    st.write(df)
    
    # Provide options to change column datatypes
    st.write("Change Column Datatypes:")
    new_dtypes = {}
    for column in df.columns:
        dtype = st.selectbox(f"Select datatype for column {column}", 
                             ['int64', 'float64', 'object', 'bool', 'datetime64[ns]'], index=2)
        new_dtypes[column] = dtype
    
    # Apply the new datatypes
    for column, dtype in new_dtypes.items():
        df[column] = df[column].astype(dtype)
    
    # Input box for table name
    table_name = st.text_input("Enter the table name")
    
    # Submit button to write the dataframe to PostgreSQL
    if st.button("Submit"):
        try:
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            st.success(f"Data loaded successfully into table '{table_name}'")
        except Exception as e:
            st.error(f"Error: {e}")
