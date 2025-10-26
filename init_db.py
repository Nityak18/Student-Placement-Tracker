import sqlite3

# Connect to database
connection = sqlite3.connect('database.db')

# Read schema.sql
with open('schema.sql') as f:
    connection.executescript(f.read())

connection.commit()
connection.close()

print("✅ Database initialized successfully!")
