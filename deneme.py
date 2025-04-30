import mysql.connector

# Establish connection
conn = mysql.connector.connect(
    host="MYSQL1002.site4now.net",
    user="ab83bf_stcadmi",
    password="Turkiye1461.",
    database="db_ab83bf_stcadmi"
)

# Create a cursor to interact with the database
cursor = conn.cursor()

# Example: execute a query
cursor.execute("SELECT * FROM deneme")

# Fetch results
results = cursor.fetchall()
for row in results:
    print(row)

# Clean up
cursor.close()
conn.close()

print("deneme.py worked")