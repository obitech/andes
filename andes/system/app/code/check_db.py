import sqlite3

connection = sqlite3.connect('data.db')
cursor = connection.cursor()

print("Check users:")
query = "SELECT * FROM users"
for row in cursor.execute(query):
  print(row)

connection.close()