import psycopg2
import pandas as pd

class db_ops:
    def __init__(self):
        self.conn = psycopg2.connect(
            database="postgres",
            user="docker_user",
            host="localhost",
            password="dcker_user",
            port=5433
        )
        self.cur = self.conn.cursor()
        self.check_connection()

    def check_connection(self):
        # Check if the table exists
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_type = 'BASE TABLE' AND table_catalog = 'postgres' AND table_schema = 'public'
        """
        self.cur.execute(query)
        df = pd.DataFrame(self.cur.fetchall(), columns=['table_name'])
        message = "table already there"
        if 'ohlc' not in df['table_name'].values:
            # Create table if it does not exist
            query = """
                CREATE TABLE ohlc (
                    timestamp TIMESTAMP,
                    ticker VARCHAR(100),
                    open FLOAT,
                    high FLOAT,
                    low FLOAT,
                    close FLOAT,
                    volume BIGINT
                );
            """
            self.cur.execute(query)
            self.conn.commit()
            message = "table created"
        print(message)

    def insert_df(self, table, df):
        # Insert DataFrame into the table
        for index, row in df.iterrows():
            query = f"""
                INSERT INTO {table} (timestamp, ticker, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            self.cur.execute(query, tuple(row))
        self.conn.commit()
        print("Data inserted successfully")

    def truncate_table(self, table: str = None):
        if table:
            query = f"""
                TRUNCATE TABLE {table};
            """
            self.cur.execute(query)
            self.conn.commit()
            print("TRUNCATED")
        else:
            print("no table name provided")

    def __del__(self):
        # Close the cursor and connection
        self.cur.close()
        self.conn.close()

