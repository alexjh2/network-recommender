import pandas as pd
import duckdb
import os

def load_profiles(csv_path='data/users.csv', db_path='data/users.db'):
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    profiles = pd.read_csv(csv_path)
    conn = duckdb.connect(db_path)
    conn.execute("CREATE OR REPLACE TABLE users AS SELECT * FROM profiles")
    print(conn.execute("SELECT * FROM users").df())
    conn.close()
    print("DuckDB table created and saved to", db_path)

load_profiles()









"""
def load_profiles(csv_file_path=None, google_sheet_url=None, table_name="users"):
    if not csv_file_path and not google_sheet_url:
        print("Error: Please provide valid CSV File Path or Google Sheet URL")
        return

    conn = duckdb.connect(database='users.db', read_only=False)
    #print(f"Connected to DuckDB")

    df = None
    if csv_file_path:
        try:
            df = pd.read_csv(csv_file_path)
            print(f"Successfully loaded data from local CSV: {csv_file_path}")
        except FileNotFoundError:
            print(f"Error: CSV file not found at {csv_file_path}")
            return
        except pd.errors.EmptyDataError:
            print(f"Error: CSV file empty at {csv_file_path}")
            return
        except Exception as e:
            print(f"An error occurred while reading the CSV file: {e}")
            return
    
    elif google_sheet_url:
        print(f"Loading data from Google Sheet URL: {google_sheet_url}")
        try:
            df = pd.read_csv(google_sheet_url)
            print(f"Successfully loaded data from Google Sheet: {google_sheet_url}")
        except Exception as e:
            print(f"An error occurred while reading the Google Sheet: {e}")
            return
    
    if df is not None:
        conn.register("profiles_df", df)
        print(f"Pandas DataFrame registered as a DuckDB view 'profiles_df'")
        try:
            conn.sql(f"CREATE TABLE {table_name} AS SELECT * FROM profiles_df")
            print(f"Successfully created DuckDB table {table_name} from the DataFrame")
        except Exception as e:
            print(f"An error occured while creating the DuckDB table: {e}")
    else:
        print("No data loaded")
    
    conn.close()
    print("DuckDB connection closed")

load_profiles('data/users.csv')
print(conn.execute("SELECT * FROM users").df())
"""