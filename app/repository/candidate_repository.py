import mysql.connector

class CandidateRepository:

    def __init__(self, db_connection):
        self.db_connection = db_connection

    def insert_candidate(self, candidate_data):
        cursor = self.db_connection.cursor()
        try:
            # Insert candidate details
            cursor.execute("""
                INSERT INTO Candidates (first_name, last_name, email, phone_number, experience, resume)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                candidate_data.get('first_name'),
                candidate_data.get('last_name'),
                candidate_data.get('email'),
                candidate_data.get('phone_number'),
                candidate_data.get('experience'),
                candidate_data.get('resume')
            ))
            # Get the candidate ID of the newly inserted candidate
            candidate_id = cursor.lastrowid

            self.db_connection.commit()

            # Insert candidate's skills if provided
            if 'skills' in candidate_data and candidate_data['skills']:
                self.insert_candidate_skills(candidate_id, candidate_data['skills'])

            return candidate_id

        except mysql.connector.Error as err:
            self.db_connection.rollback()
            raise Exception(f"Error creating candidate: {err}")
        finally:
            cursor.close()

    def insert_candidate_skills(self, candidate_id, skills):
        cursor = self.db_connection.cursor()
        try:
            for skill in skills:
                cursor.execute("""
                    INSERT INTO CandidateSkills (candidate_id, skill_name) 
                    VALUES (%s, %s)
                """, (candidate_id, skill))

            self.db_connection.commit()  # Commit after inserting all skills

        except mysql.connector.Error as err:
            self.db_connection.rollback()
            raise Exception(f"Error inserting candidate skills: {err}")
        finally:
            cursor.close()
