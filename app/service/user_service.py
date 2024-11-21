from app.repository.user_repository import UserRepository  # Adjust the import based on your repository structure
from config import MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE_NAME
from mysql.connector import connect
import bcrypt

class UserService:
    
    def __init__(self):
        self.db_connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE_NAME
        )
        self.user_repository = UserRepository(self.db_connection)


    def create_user(self, user_data):
        #password encription
        hashed_password = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())

        # user_data['password'] = user_data['password'] 
        user_data['password'] = hashed_password
        return self.user_repository.insert_user(user_data)

    def get_user_by_id(self, employee_id):
        return self.user_repository.fetch_user_by_id(employee_id)
    
    def update_user(self, employee_id, user_data):
        return self.user_repository.update_user(employee_id, user_data)
    
    def get_user_by_credentials(self, username=None, email=None, employeeId=None):
        return self.user_repository.fetch_user_by_credentials(username, email, employeeId)
    
    def get_all_users(self):
        return self.user_repository.fetch_all_users()