import mysql.connector

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Rakshita_7229-",
            database="student_result_db"
        )
        print("✅ Connected to database successfully!")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
        return None

# Call function to test it
get_db_connection()
