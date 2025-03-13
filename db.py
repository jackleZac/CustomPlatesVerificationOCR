# This file handles MySQL connections and queries
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def get_all_plates():
    connection = get_db_connection()
    if not connection:
        return []
    cursor = connection.cursor()
    cursor.execute("SELECT plate_number FROM trucks")
    plates = [plate[0] for plate in cursor.fetchall()]
    cursor.close()
    connection.close()
    return plates
