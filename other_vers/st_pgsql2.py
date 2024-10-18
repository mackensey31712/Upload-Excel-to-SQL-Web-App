import streamlit as st
import pandas as pd
import sqlite3
import gspread
from google.oauth2.service_account import Credentials
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="SRR Raw Data", page_icon=":bar_chart:", layout="wide")

st.title("SRR Raw Data")

# Initialize session state for refresh
if "refresh_data" not in st.session_state:
    st.session_state.refresh_data = False
if "default_table_index_adjusted" not in st.session_state:
    st.session_state.default_table_index_adjusted = False

# Add a "Refresh Data" button
if st.button("Refresh Data"):
    st.cache_data.clear()
    st.session_state.refresh_data = True
    st.session_state.default_table_index_adjusted = False

# Establish connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Read data from the specified worksheet
if st.session_state.refresh_data:
    df = conn.read(worksheet="Response")
    st.session_state.refresh_data = False
    st.session_state.df = df  # Update session state with the new data
    st.session_state.default_table_index_adjusted = False
else:
    if "df" not in st.session_state:
        st.session_state.df = conn.read(worksheet="Response")
    df = st.session_state.df

# Radio button to select the mode
mode = st.radio("Select Mode", ("Default Table", "SQL"))

def update_google_sheet(updated_df, worksheet_name="Response"):
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("path/to/credentials.json", scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("Your Google Sheet Name").worksheet(worksheet_name)
    
    # Update the Google Sheet with the new data
    sheet.clear()
    sheet.update([updated_df.columns.values.tolist()] + updated_df.values.tolist())

if mode == "Default Table":
    if not st.session_state.default_table_index_adjusted:
        df.index = df.index + 1  # Adjust index to start from 1
        st.session_state.default_table_index_adjusted = True
    edited_df = st.data_editor(df, num_rows="dynamic")

    # Add a button to confirm changes
    if st.button("Confirm Changes"):
        # Compare the original and edited DataFrames
        changes = edited_df[edited_df != df].dropna(how='all')
        
        if not changes.empty:
            # Reset index before writing back to Google Sheets
            changes.index = changes.index - 1
            for index, row in changes.iterrows():
                update_google_sheet(edited_df.loc[[index]])
            st.success("Changes confirmed and data updated!")
        else:
            st.info("No changes detected.")
        
        st.session_state.df = edited_df
        st.session_state.default_table_index_adjusted = False

elif mode == "SQL":
    query = st.text_area("Enter SQL Query", "")

    if st.button("Query"):
        if query.strip():
            # Load the DataFrame into an in-memory SQLite database
            sqlite_conn = sqlite3.connect(":memory:")
            df.to_sql("df", sqlite_conn, index=False, if_exists="replace")
            
            if query.strip().upper().startswith("SELECT"):
                queried_df = pd.read_sql_query(query, sqlite_conn)
                queried_df.index += 1  # Adjust index to start from 1
                st.session_state.queried_df = queried_df
            elif query.strip().upper().startswith("UPDATE"):
                sqlite_conn.execute(query)
                sqlite_conn.commit()
                updated_df = pd.read_sql_query("SELECT * FROM df", sqlite_conn)
                updated_df.index += 1  # Adjust index to start from 1
                st.session_state.queried_df = updated_df
                st.success("Update query executed. Review changes below.")
            else:
                st.error("Only SELECT and UPDATE queries are supported.")
            
            sqlite_conn.close()

    # Display the queried data editor if there is a queried_df in the session state
    if "queried_df" in st.session_state:
        st.write("Query Results:")
        edited_df = st.data_editor(st.session_state.queried_df, num_rows="dynamic")

        # Add a button to confirm changes for the queried data
        if st.button("Confirm Changes"):
            if query.strip().upper().startswith("SELECT"):
                # Compare the original and edited DataFrames
                changes = edited_df[edited_df != st.session_state.queried_df].dropna(how='all')
                
                if not changes.empty:
                    # Reset index before writing back to Google Sheets
                    changes.index = changes.index - 1
                    for index, row in changes.iterrows():
                        update_google_sheet(edited_df.loc[[index]])
                    st.success("Changes confirmed and data updated!")
                else:
                    st.info("No changes detected.")
                
                st.session_state.df = edited_df
            elif query.strip().upper().startswith("UPDATE"):
                # Find the rows that were updated
                updated_rows = edited_df[edited_df != st.session_state.queried_df].dropna()
                if not updated_rows.empty:
                    # Write only the modified rows back to the Google Sheets
                    for index, row in updated_rows.iterrows():
                        update_google_sheet(edited_df.loc[[index]])
                    st.success("Changes confirmed and data updated!")
                else:
                    st.info("No changes to confirm.")
            st.session_state.df = edited_df

# Ensure only the relevant table is shown based on the mode
if mode == "Default Table":
    if "queried_df" in st.session_state:
        del st.session_state.queried_df
