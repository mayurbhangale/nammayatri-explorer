import pandas as pd
import sqlite3
import requests
import constants

def get_api_data(url):
    response = requests.get(url)
    df = pd.read_json(response.text)
    return df

def create_connection():
    conn = sqlite3.connect("namma_yatri.db")
    return conn

def create_table(conn):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS hourly_data (
        ac_num INTEGER,
        date DATE,
        hour INTEGER,
        srch_rqst INTEGER,
        srch_fr_q INTEGER,
        srch_which_got_q INTEGER,
        booking INTEGER,
        done_ride INTEGER,
        earning INTEGER,
        cancel_ride INTEGER,
        cnvr_rate FLOAT,
        bkng_cancel_rate FLOAT,
        q_accept_rate FLOAT,
        PRIMARY KEY (ac_num, date, hour)
    )
    """
    conn.execute(create_table_query)

def insert_data(conn, data):
    insert_query = """
    INSERT OR IGNORE INTO hourly_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    conn.executemany(insert_query, data)
    conn.commit()

def runner():
    df = get_api_data(constants.LIVE_DATA)
    
    conn = create_connection()
    create_table(conn)

    primary_key_columns = ["ac_num", "date", "hour"]
    duplicates_mask = df.duplicated(subset=primary_key_columns, keep="first")

    non_duplicates_df = df[~duplicates_mask]

    if not non_duplicates_df.empty:
        data_to_insert = non_duplicates_df.to_records(index=False).tolist()
        insert_data(conn, data_to_insert)

    conn.close()