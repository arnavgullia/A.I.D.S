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

# Default configuration (can be overridden by environment variables)
DB_HOST = os.getenv("AEGIS_MYSQL_HOST", "localhost")
DB_PORT = int(os.getenv("AEGIS_MYSQL_PORT", 3306))
DB_USER = os.getenv("AEGIS_MYSQL_USER", "root") # Default to root for setup
DB_PASSWORD = os.getenv("AEGIS_MYSQL_PASSWORD", "")
DB_NAME = os.getenv("AEGIS_MYSQL_DATABASE", "aegis_db")

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "shared", "schema.sql")

def run_setup():
    print("=========================================")
    print("   Project Aegis - MySQL Setup Script    ")
    print("=========================================")
    
    # 1. Connect to MySQL Server (no database selected yet)
    print(f"[Setup] Connecting to MySQL at {DB_HOST}:{DB_PORT} as '{DB_USER}'...")
    connection = None
    try:
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD
            )
        except Error as e:
            if e.errno == 1045: # Access denied
                print("[Setup] Access denied. Password required.")
                from getpass import getpass
                password = getpass(f"Enter password for {DB_USER}: ")
                connection = mysql.connector.connect(
                    host=DB_HOST,
                    port=DB_PORT,
                    user=DB_USER,
                    password=password
                )
            else:
                raise e
                
        if connection.is_connected():
            print("[Setup] Connection successful.")
            cursor = connection.cursor()
            
            # 2. Create Database
            print(f"[Setup] Creating database '{DB_NAME}' if not exists...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            print("[Setup] Database created/verified.")
            
            # 3. Create User if needed (optional, often skipped if using root)
            # For simplicity, we'll assume the user provided HAS access or we use root
            
            # 4. Use the database
            cursor.execute(f"USE {DB_NAME}")
            
            # 5. Run Schema Script
            print(f"[Setup] Executing schema from {SCHEMA_FILE}...")
            if not os.path.exists(SCHEMA_FILE):
                print(f"[Error] Schema file not found at {SCHEMA_FILE}")
                return
            
            with open(SCHEMA_FILE, 'r') as f:
                schema_sql = f.read()
            
            # Split by command (simple logic, might break on complex stored procs with ; inside strings)
            # Better: read file and execute statement by statement if possible, or use Multi=True
            # schema.sql uses DELIMITER, which python connector might not handle natively with split(';')
            # We will use split(';') but special handling for DELIMITER is tricky.
            # Simplified approach: Since schema.sql is relatively simple, we can try Multi=True 
            # OR just read it and try to execute chunks. 
            
            # Let's try splitting by ';' for standard statements
            # Note: The Stored Procedure definition uses DELIMITER // ... END //
            # We might need to handle that manually or remove it for this basic setup script if it causes issues.
            # For now, let's try iterating.
            
            # Actually, multi=True allows multiple statements in one execute call
            # cursor.execute(schema_sql, multi=True)
            # But stored procedures/DELIMITER logic is client-side (mysql cli).
            # We need to strip DELIMITER lines.
            
            statements = []
            delimiter = ";"
            current_statement = []
            
            lines = schema_sql.split('\n')
            for line in lines:
                stripped = line.strip()
                if not stripped or stripped.startswith("--"):
                    continue
                
                if stripped.upper().startswith("DELIMITER"):
                    delimiter = stripped.split()[1]
                    continue
                
                current_statement.append(line)
                
                if stripped.endswith(delimiter):
                    # Found end of statement
                    stmt = "\n".join(current_statement)
                    # Remove the delimiter from the end
                    stmt = stmt.rsplit(delimiter, 1)[0]
                    statements.append(stmt)
                    current_statement = []
            
            # Execute each statement
            count = 0
            for stmt in statements:
                if not stmt.strip(): continue
                try:
                    cursor.execute(stmt)
                    # cursor.next_result() is only for multi=True, which we aren't using here per statement
                    count += 1
                except Error as e:
                    print(f"[Warning] Error executing statement (might be safe to ignore if exists): {e}")
                    # print(f"Statement: {stmt[:50]}...")

            connection.commit()
            print(f"[Setup] Executed {count} statements successfully.")
            
            print("=========================================")
            print("       SETUP COMPLETE SUCCESSFULY        ")
            print("=========================================")
            print(f"You can now run the server with: set AEGIS_DB_TYPE=mysql && python api_server.py")
            
    except Error as e:
        print(f"[Error] MySQL Connection failed: {e}")
        print("Please ensure MySQL server is running and credentials are correct.")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    run_setup()
