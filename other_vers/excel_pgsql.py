import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine

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

# Load the Excel file
excel_file = 'Open Escalations.xlsx'
df = pd.read_excel(excel_file, sheet_name='data')

# Write the dataframe to the PostgreSQL table
df.to_sql('open_escalations', engine, if_exists='replace', index=False)

print("Data loaded successfully")
