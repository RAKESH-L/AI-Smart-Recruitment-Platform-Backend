from app.repository.candidate_repository import CandidateRepository
from mysql.connector import connect
from config import MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE_NAME

class CandidateService:

    def __init__(self):
        self.db_connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE_NAME
        )
        self.candidate_repository = CandidateRepository(self.db_connection)

    def create_candidate(self, candidate_data):
        return self.candidate_repository.insert_candidate(candidate_data)
