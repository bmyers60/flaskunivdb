import sqlite3

# Create or connect to the database
conn = sqlite3.connect("university.db")
cursor = conn.cursor()

# Read and execute the DDL script (create tables)
with open("univ-ddl.sql", "r") as ddl_file:
    ddl_script = ddl_file.read()
    cursor.executescript(ddl_script)
    print("Tables created successfully.")

# Read and execute the DML script (insert data)
with open("univ-dml.sql", "r") as dml_file:
    dml_script = dml_file.read()
    cursor.executescript(dml_script)
    print("Data inserted successfully.")

# Commit and close
conn.commit()
conn.close()

print("Database setup complete.")
