import mysql.connector
import json  # Ensure you import json

class ReportRepository:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def insert_report(self, report_data):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO Report (reportName, createdBy, filters, fields_included, data)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                report_data['reportName'],
                report_data['createdBy'],
                json.dumps(report_data.get('filters', None)),  # Serialize to JSON string
                json.dumps(report_data.get('fields_included', None)),  # Serialize to JSON string
                json.dumps(report_data.get('data', None))  # Serialize to JSON string
            ))
            self.db_connection.commit()
            return cursor.lastrowid  # Return the ID of the newly inserted report
        except mysql.connector.Error as err:
            self.db_connection.rollback()
            raise Exception(f"Error inserting report: {err}")
        finally:
            cursor.close()

    def fetch_all_reports(self):
        cursor = self.db_connection.cursor(dictionary=True)  # Use dictionary for JSON response
        try:
            cursor.execute("SELECT * FROM Report")
            reports = cursor.fetchall()  # Fetch all reports
            return reports  # Return fetched reports as a list of dictionaries
        except mysql.connector.Error as err:
            raise Exception(f"Error fetching reports: {err}")
        finally:
            cursor.close()