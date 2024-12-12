from app.repository.application_repository import ApplicationRepository
from mysql.connector import connect
from config import MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE_NAME
import mysql.connector
from datetime import datetime
import os

class ApplicationService:

    def __init__(self):
        self.db_connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE_NAME
        )
        self.application_repository = ApplicationRepository(self.db_connection)
        
    def _create_connection(self):
        """ Helper method to create a new DB connection """
        return connect(
            host=MYSQL_HOST,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE_NAME
        )

    def create_application(self, application_data, skills):
        # Insert application first and get the application_id
        application_id = self.application_repository.insert_application(application_data)

        # Insert candidate skills if provided
        if skills:
            self.application_repository.insert_candidate_skills(application_id, skills)

        return application_id
    
    def get_job_description_by_job_id(self, job_id):
        return self.application_repository.get_job_description_by_job_id(job_id)

    def check_existing_application(self, job_id, phone_number):
        return self.application_repository.application_exists(job_id, phone_number)
    
    def get_applications_by_job_id(self, job_id, job_title=None, status=None):
        return self.application_repository.fetch_applications_by_job_id(job_id, job_title=None, status=None)
    
    def update_application_status(self, application_id, status):
        return self.application_repository.update_status(application_id, status)

    
            
    def accept_offer(self, application_id, offer_accepted_date):
        cursor = self.db_connection.cursor()
        try:
            # 1. Retrieve the current status and job ID for the specified application
            cursor.execute("""
                SELECT job_id, status FROM Applications WHERE id = %s
            """, (application_id,))
            result = cursor.fetchone()

            if result:
                job_id, current_status = result

                # 2. Check if the current status is 'offered'
                if current_status == 'offered':
                    # 3. Update the status to 'accepted' and set offer_accepted_date
                    cursor.execute("""
                        UPDATE Applications
                        SET status = 'accepted', offer_accepted_date = %s
                        WHERE id = %s
                    """, (offer_accepted_date, application_id))

                    # Check if the row was actually updated
                    if cursor.rowcount == 0:
                        return False  # No rows updated, which should not happen here

                    # 4. Check how many accepted applications exist for the same job
                    cursor.execute("""
                        SELECT COUNT(*) FROM Applications WHERE job_id = %s AND status = 'accepted'
                    """, (job_id,))
                    accepted_count = cursor.fetchone()[0]

                    # 5. If this is the first acceptance, insert performance analytics
                    if accepted_count == 1:  # This is now the first accepted application
                        # Get the job posting date for calculating Time-to-Hire
                        cursor.execute("""
                            SELECT created_at FROM Jobs WHERE job_id = %s
                        """, (job_id,))
                        job_posting_date = cursor.fetchone()[0]

                        # Calculate Time-to-Hire
                        time_to_hire = (datetime.strptime(offer_accepted_date, '%Y-%m-%d %H:%M:%S') - job_posting_date).days

                        # Insert performance analytics
                        self.insert_performance_analytics(job_id, time_to_hire)

                    self.db_connection.commit()
                    return True  # The status was successfully updated to 'accepted'

                else:
                    return False  # Current status is not 'offered'
            else:
                raise Exception("Application not found")

        except mysql.connector.Error as err:
            self.db_connection.rollback()
            raise Exception(f"Error accepting offer: {err}")
        finally:
            cursor.close()

    def insert_performance_analytics(self, job_id, time_to_hire):
        cursor = self.db_connection.cursor()
        try:
            # Insert the metric into PerformanceAnalytics
            cursor.execute("""
                INSERT INTO PerformanceAnalytics (job_id, metric_name, metric_value)
                VALUES (%s, %s, %s)
            """, (job_id, 'Time-to-Hire', time_to_hire))
            self.db_connection.commit()
        except mysql.connector.Error as err:
            self.db_connection.rollback()
            raise Exception(f"Error inserting performance analytics: {err}")
        finally:
            cursor.close()
            
    def get_applications_by_creator(self, created_by, job_title=None, status=None):
        return self.application_repository.fetch_applications_by_creator(created_by, job_title, status)
    
    def get_applications_by_candidateId(self, candidate_id, job_title=None, status=None):
        return self.application_repository.fetch_applications_by_candiadteId(candidate_id, job_title, status)
    
    def get_resume_by_application_id(self, application_id):
        # Create a new connection for this operation
        db_connection = self._create_connection()
        application_repository = ApplicationRepository(db_connection)

        # Get the resume path from the repository
        resume_path = application_repository.get_resume_path_by_application_id(application_id)

        if resume_path and os.path.exists(resume_path):
            with open(resume_path, 'rb') as resume_file:
                resume_content = resume_file.read()
            db_connection.close()  # Close the connection after use
            return resume_content, 200
        else:
            db_connection.close()  # Ensure the connection is closed on failure
            if resume_path is None:
                return {"error": "Application not found"}, 404
            else:
                return {"error": "Resume file not found"}, 404