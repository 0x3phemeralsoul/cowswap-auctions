import sqlite3, os
from dotenv import load_dotenv


load_dotenv()

# Create a new SQLite database file
new_db_conn = sqlite3.connect('new_db.db')
new_db_conn.close()

# Open connections to the old and new databases
old_db_conn = sqlite3.connect(os.getenv("DATABASE_URL")[10::])

# Create a cursor to execute SQL commands
cursor = old_db_conn.cursor()

# Get a list of all table names in the old database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
table_names = cursor.fetchall()

# Open a connection to the new database
new_db_conn = sqlite3.connect('new_db.db')
new_cursor = new_db_conn.cursor()

# Copy the schema (structure) of each table and indexes from the old database to the new database
for table_name in table_names:
    table_name = table_name[0]
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    create_table_sql = cursor.fetchone()[0]
    new_cursor.execute(create_table_sql)

    # Get the names of indexes associated with the table in the old database
    cursor.execute(f"PRAGMA index_list('{table_name}');")
    index_info = cursor.fetchall()
    
# Create the same indexes in the new database
for index in index_info:
    index_name = index[1]
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='index' AND name='{index_name}';")
    create_index_sql = cursor.fetchone()[0]
    new_cursor.executescript(create_index_sql)  # Use executescript() for index creation

# Commit and close the connections
new_db_conn.commit()
new_db_conn.close()
old_db_conn.close()
