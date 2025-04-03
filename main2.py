import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="xyz",
        database="soham",
        port=3306  # Ensure correct port
    )
    print("✅ Connected to MySQL successfully!")
    conn.close()
except mysql.connector.Error as err:
    print(f"❌ MySQL Connection Error: {err}")
