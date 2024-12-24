
import mysql.connector
from app.repository.report_repository import ReportRepository
from config import MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE_NAME

class ReportService:
    def __init__(self):
        self.db_connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE_NAME
        )
        self.report_repository = ReportRepository(self.db_connection)

    def create_report(self, report_data):
        return self.report_repository.insert_report(report_data)

    def get_all_reports(self):
        return self.report_repository.fetch_all_reports()