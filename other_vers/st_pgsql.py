import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, inspect

st.set_page_config(page_title="Database Data Editor", page_icon=":bar_chart:", layout="wide")

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

# Load available tables from PostgreSQL
@st.cache_data(ttl=600)
def load_tables():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return tables

# Load data from PostgreSQL for a specific table
@st.cache_data(ttl=600)
def load_data(table_name):
    query = f'SELECT * FROM "{table_name}"'
    df = pd.read_sql(query, engine)
    return df

# Save data to PostgreSQL for a specific table
def save_data(table_name, df):
    # Write the dataframe back to the specified table
    df.to_sql(table_name, engine, if_exists='replace', index=False)

# Streamlit app layout
tables = load_tables()
selected_table = st.selectbox("Select a table", tables)

if selected_table:
    st.title(f"{selected_table} Data Editor")

    # Load data
    data = load_data(selected_table)

    # Display editable dataframe
    edited_data = st.data_editor(data, num_rows="dynamic")

    # Save changes to database
    if st.button("Confirm Changes"):
        save_data(selected_table, edited_data)
        st.success(f"Data for {selected_table} updated successfully")
