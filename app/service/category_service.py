# app/service/category_service.py

import mysql.connector
from app.repository.category_repository import CategoryRepository
from config import MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE_NAME

class CategoryService:
    def __init__(self):
        self.db_connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE_NAME
        )
        self.category_repository = CategoryRepository(self.db_connection)

    def create_category(self, category_data):
        return self.category_repository.insert_category(category_data)
    
    def get_all_categories(self):
        return self.category_repository.fetch_all_categories()
