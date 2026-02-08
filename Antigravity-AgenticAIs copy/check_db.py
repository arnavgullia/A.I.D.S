import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("[Warning] python-dotenv not installed. Environment variables might not load from .env")

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    print("[Error] mysql-connector-python not installed. Run: pip install mysql-connector-python")
    sys.exit(1)

# Configuration from .env
DB_HOST = os.getenv("AEGIS_MYSQL_HOST", "localhost")
DB_PORT = int(os.getenv("AEGIS_MYSQL_PORT", 3306))
DB_USER = os.getenv("AEGIS_MYSQL_USER", "root")
DB_PASSWORD = os.getenv("AEGIS_MYSQL_PASSWORD", "")
DB_NAME = os.getenv("AEGIS_MYSQL_DATABASE", "aegis_db")

def check_db():
    print(f"Connecting to database '{DB_NAME}' at {DB_HOST}:{DB_PORT}...")
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        if connection.is_connected():
            print("Connection Successful!")
            cursor = connection.cursor(dictionary=True)
            
            print("\n--- Tables in Database ---")
            cursor.execute("SHOW TABLES")
            for row in cursor.fetchall():
                print(row)
            
            print("\n--- Testing Apophis Query ---")
            cursor.execute("SELECT * FROM asteroid WHERE Name LIKE '%Apophis%' OR Asteroid_ID LIKE '%Apophis%'")
            rows = cursor.fetchall()
            if rows:
                print(f"Found: {rows[0]}")
            else:
                print("Not found")
            
            cursor.close()
            connection.close()
            
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
