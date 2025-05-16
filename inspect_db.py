import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in the database:", tables)

cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

columns = [description[0] for description in cursor.description]
print("\nColumns:", columns)

print("\nData in users table:")
for row in rows:
    print(row)

# Close the connection
conn.close()