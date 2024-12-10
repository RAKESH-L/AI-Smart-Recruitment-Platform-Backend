from app.repository.job_repository import JobRepository
from mysql.connector import connect
from config import MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE_NAME
import mysql.connector
from app.service.email_service import EmailService
from app.repository.user_repository import UserRepository


class JobService:
    
    def __init__(self):
        self.db_connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE_NAME
        )
        self.job_repository = JobRepository(self.db_connection)
        self.user_repository = UserRepository(self.db_connection)  # Create a UserRepository instance
        self.email_service = EmailService()  # Initialize the email service
        
    def create_job(self, job_data):
        # Insert the job into the database
        # job_id = self.job_repository.insert_job(job_data)
        job_id = 1

        # Fetch the user's email based on the created_by ID
        created_by_id = job_data['created_by']  # Get created_by ID from job_data
        user = self.user_repository.fetch_user_by_id(created_by_id)  # Fetch email
        user_email = user['email']
        
        # Send an email notification if the email is found
        if user_email:
            subject = "New Job Created"
            body = f"""
            A new job has been created successfully!
            
            Job ID: {job_id}
            Title: {job_data['title']}
            Description: {job_data['description']}
            Department: {job_data.get('department', 'N/A')}
            Location: {job_data.get('location', 'N/A')}
            Status: {job_data.get('status', 'open')}
            
            Thank you!
            """
            self.email_service.send_email(user_email, subject, body)

        return job_id

    def add_job_skills(self, job_id, skills):
        return self.job_repository.insert_job_skills(job_id, skills)

    def get_jobs_by_creator(self, created_by, status=None):
        return self.job_repository.fetch_jobs_by_creator(created_by, status)
    
    def update_job(self, job_id, job_data):
        return self.job_repository.update_job(job_id, job_data)

    def update_job_skills(self, job_id, skills):
        return self.job_repository.update_job_skills(job_id, skills)
    
    def delete_job(self, job_id):
        return self.job_repository.delete_job(job_id)
    
    def log_job_action(self, job_id, action, performed_by):
        # Insert a log entry into JobPostingLog
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO JobPostingLog (job_id, action, performed_by)
                VALUES (%s, %s, %s)
            """, (job_id, action, performed_by))
            self.db_connection.commit()
        except mysql.connector.Error as err:
            self.db_connection.rollback()
            raise Exception(f"Error logging job action: {err}")
        finally:
            cursor.close()
            
    def get_job_by_id(self, job_id):
        cursor = self.db_connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM Jobs WHERE job_id = %s", (job_id,))
            job = cursor.fetchone()
            return job  # This will return job details including 'created_by'
        except mysql.connector.Error as err:
            raise Exception(f"Error fetching job by ID: {err}")
        finally:
            cursor.close()
            
    def get_job_posting_logs(self):
        return self.job_repository.fetch_job_posting_logs()
    
    def get_job_posting_logs_by_action(self, action):
        return self.job_repository.fetch_job_posting_logs_by_action(action)
    
    def get_job_logs(self, performed_by_id):
        """Get job logs based on the performed_by ID."""
        return self.job_repository.get_job_logs_by_performed_by(performed_by_id)
    