# app/repository/category_repository.py

import mysql.connector

class CategoryRepository:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def insert_category(self, category_data):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO Category (category_type, category_name, status)
                VALUES (%s, %s, %s)
            """, (
                category_data.get('category_type'),
                category_data.get('category_name'),
                category_data.get('status', 'active')  # Default to 'active' if not provided
            ))

            # Commit the transaction
            self.db_connection.commit()
            return cursor.lastrowid  # Return the ID of the newly inserted category
        except mysql.connector.Error as err:
            self.db_connection.rollback()
            raise Exception(f"Error inserting category: {err}")
        finally:
            cursor.close()

    def fetch_all_categories(self):
        cursor = self.db_connection.cursor(dictionary=True)  # Use dictionary cursor for readable output
        try:
            cursor.execute("SELECT * FROM Category")  # Fetch all fields from the Category table
            categories = cursor.fetchall()
            return categories  # Return all categories as a list of dictionaries
        except mysql.connector.Error as err:
            raise Exception(f"Error fetching categories: {err}")
        finally:
            cursor.close()