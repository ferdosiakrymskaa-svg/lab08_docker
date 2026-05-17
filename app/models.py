import os
import mysql.connector

class ItemModel:
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'db'),
            'port': 3306,
            'user': os.getenv('DB_USER', 'user'),
            'password': os.getenv('DB_PASSWORD', 'userpass'),
            'database': os.getenv('DB_NAME', 'mydb'),
            'charset': 'utf8mb4',          # <-- вот что решит проблему
            'collation': 'utf8mb4_unicode_ci'
        }

    def get_all_items(self):
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT name FROM items')
            items = cursor.fetchall()
            cursor.close()
            conn.close()
            return items
        except Exception as e:
            print(f"Error: {e}")
            return []
