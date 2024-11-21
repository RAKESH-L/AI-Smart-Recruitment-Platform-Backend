from app.repository.interview_repository import InterviewRepository
from app.repository.application_repository import ApplicationRepository
from mysql.connector import connect
from config import MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE_NAME

class InterviewService:

    def __init__(self):
        self.db_connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE_NAME
        )
        self.interview_repository = InterviewRepository(self.db_connection)
        self.application_repository = ApplicationRepository(self.db_connection)  

    def create_interview(self, interview_data):
        # Check if an interview of the same type is already scheduled
        has_scheduled_interview = self.interview_repository.check_existing_scheduled_interview(
            interview_data['application_id'], 
            interview_data['job_id'], 
            interview_data['type']
        )

        if has_scheduled_interview:
            raise Exception("Interview is already scheduled")

        # Insert the interview into the database
        interview_id = self.interview_repository.insert_interview(interview_data)

        # Update the application status to "interviewing"
        application_id = interview_data['application_id']  # Get application_id from interview_data
        self.application_repository.update_status(application_id, "interviewing")

        return interview_id
    
    def update_interview(self, interview_id, interview_data):
        # Call the repository to update the interview
        return self.interview_repository.update_interview(interview_id, interview_data)
    
    def get_interviews_by_interviewer(self, interviewer_id):
        """ Fetch interviews by the interviewer's ID """
        return self.interview_repository.fetch_interviews_by_interviewer(interviewer_id)
    
    def get_interviews_by_owner(self, owner_id):
        """ Fetch interviews by owner ID """
        return self.interview_repository.fetch_interviews_by_owner(owner_id)
    
    def get_interviews_by_application(self, application_id):
        """ Fetch interviews by application ID """
        return self.interview_repository.fetch_interviews_by_application(application_id)
    
    def get_interviews_by_job_and_owner(self, job_id, owner_id):
        """ Fetch interviews by job ID and owner ID """
        return self.interview_repository.fetch_interviews_by_job_and_owner(job_id, owner_id)
    
    def get_interviews_by_job_and_interview(self, job_id, interviewer_id):
        """ Fetch interviews by job ID and interview ID """
        return self.interview_repository.fetch_interviews_by_job_and_interview(job_id, interviewer_id)

