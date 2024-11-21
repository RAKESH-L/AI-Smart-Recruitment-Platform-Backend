import mysql.connector
from config import MYSQL_DATABASE_NAME
import bcrypt

class UserRepository:

    def __init__(self, db_connection):
        self.db_connection = db_connection

    def insert_user(self, user_data):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO Users (employee_id, full_name, username, password, phone_number, role, email) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_data['employee_id'], user_data['full_name'], user_data['username'], user_data['password'], user_data['phone_number'], user_data['role'], user_data['email']))
            self.db_connection.commit()
            return cursor.lastrowid  # Return the ID of the newly inserted user
        except mysql.connector.Error as err:
            self.db_connection.rollback()
            raise Exception(f"Error inserting user: {err}")
        finally:
            cursor.close()
            
    def fetch_user_by_id(self, employee_id):
        cursor = self.db_connection.cursor(dictionary=True)  # Use dictionary cursor for easy conversion to JSON
        try:
            cursor.execute("SELECT * FROM Users WHERE employee_id = %s", (employee_id,))
            user = cursor.fetchone()  # Fetch a single record
            return user
        except mysql.connector.Error as err:
            raise Exception(f"Error fetching user: {err}")
        finally:
            cursor.close()
            
    def update_user(self, employee_id, user_data):
        cursor = self.db_connection.cursor()
        try:
            # You can update fields based on your requirements
            update_fields = []
            update_values = []

            if 'full_name' in user_data:
                update_fields.append("full_name = %s")
                update_values.append(user_data['full_name'])
            if 'username' in user_data:
                update_fields.append("username = %s")
                update_values.append(user_data['username'])
            if 'password' in user_data:  
                update_fields.append("password = %s")
                hashed_password = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
                # update_values.append(user_data['password'])
                update_values.append(hashed_password)
            if 'phone_number' in user_data:  
                update_fields.append("phone_number = %s")
                update_values.append(user_data['phone_number'])
            if 'role' in user_data:
                update_fields.append("role = %s")
                update_values.append(user_data['role'])
            if 'email' in user_data:
                update_fields.append("email = %s")
                update_values.append(user_data['email'])

            # If no fields to update, return None
            if not update_fields:
                return None

            # Append the user ID for the WHERE clause
            update_values.append(employee_id)

            cursor.execute(f"""
                UPDATE Users
                SET {', '.join(update_fields)}
                WHERE employee_id = %s
            """, update_values)
            
            self.db_connection.commit()

            # Check if any row was updated
            if cursor.rowcount > 0:
                return True  # Indicating update was successful
            else:
                return False  # Indicating updated failed (user not found)

        except mysql.connector.Error as err:
            self.db_connection.rollback()
            raise Exception(f"Error updating user: {err}")
        finally:
            cursor.close()
            
    def fetch_user_by_credentials(self, username, email, employeeId):
        cursor = self.db_connection.cursor(dictionary=True)
        try:
            print("error in")
            # Build the query based on whether username or email is provided
            if username:
                cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
            elif email:
                cursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
            elif employeeId:
                cursor.execute("SELECT * FROM Users WHERE employee_id = %s", (employeeId,))
            else:
                return None  # Neither username nor email provided

            user = cursor.fetchone()
            return user  # Return the user record
        except mysql.connector.Error as err:
            raise Exception(f"Error fetching user: {err}")
        finally:
            cursor.close()
            
    def fetch_all_users(self):
        cursor = self.db_connection.cursor(dictionary=True)  # Use a dictionary cursor for easy JSON conversion
        try:
            cursor.execute("SELECT * FROM Users")
            users = cursor.fetchall()
            return users  # Return results as a list of dictionaries
        except mysql.connector.Error as err:
            raise Exception(f"Error fetching users: {err}")
        finally:
            cursor.close()