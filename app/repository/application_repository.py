import mysql.connector

class ApplicationRepository:

    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.cursor = self.db_connection.cursor(dictionary=True)  # Use dictionary cursor for easier result handling

    # Method to insert application
    def insert_application(self, application_data):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO Applications (job_id, first_name, last_name, email, phone_number,
                    experience, current_ctc, expected_ctc, resume, status, candidate_id, offer_accepted_date, openai_score, nlp_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                application_data.get('job_id'),
                application_data.get('first_name'),
                application_data.get('last_name'),
                application_data.get('email'),
                application_data.get('phone_number'),
                application_data.get('experience'),
                application_data.get('current_ctc'),
                application_data.get('expected_ctc'),
                application_data.get('resume'),
                application_data.get('status'),
                application_data.get('candidate_id'),
                application_data.get('offer_accepted_date'),
                application_data.get('openai_score'),
                application_data.get('nlp_score')
            ))
            self.db_connection.commit()
            return cursor.lastrowid  # Return the ID of the newly inserted application
        except mysql.connector.Error as err:
            self.db_connection.rollback()
            raise Exception(f"Error inserting application: {err}")
        finally:
            cursor.close()

    # Method to insert candidate skills
    def insert_candidate_skills(self, application_id, skills):
        cursor = self.db_connection.cursor()
        try:
            for skill in skills:
                cursor.execute("""
                    INSERT INTO CandidateSkills (application_id, skill_name)
                    VALUES (%s, %s)
                """, (application_id, skill))

            self.db_connection.commit()  # Commit after inserting all skills
        except mysql.connector.Error as err:
            self.db_connection.rollback()
            raise Exception(f"Error inserting candidate skills: {err}")
        finally:
            cursor.close()
    
    # Method to check for existing application
    def application_exists(self, job_id, phone_number):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM Applications
                WHERE job_id = %s AND phone_number = %s
            """, (job_id, phone_number))
            count = cursor.fetchone()[0]
            return count > 0  # Return True if application exists
        except mysql.connector.Error as err:
            raise Exception(f"Error checking existing application: {err}")
        finally:
            cursor.close()
            
    def fetch_applications_by_job_id(self, job_id, job_title=None, status=None):
        cursor = self.db_connection.cursor(dictionary=True)  # Use dictionary cursor for easy JSON conversion
        try:
            query = """
                SELECT a.id AS application_id,
                       a.job_id,
                       a.first_name,
                       a.last_name,
                       a.email,
                       a.phone_number,
                       a.experience,
                       a.current_ctc,
                       a.expected_ctc,
                       a.resume,
                       a.status AS application_status,
                       a.submitted_at,
                       a.updated_at,
                       a.openai_score,
                       a.nlp_score,
                       j.title AS job_title,
                       j.description AS job_description,
                       j.department AS job_department,
                       j.experience AS job_experience,
                       j.location AS job_location,
                       j.employment_type AS job_employment_type,
                       j.salary_range AS job_salary_range,
                       j.status AS job_status
                FROM Applications a
                JOIN Jobs j ON a.job_id = j.job_id
                WHERE j.job_id = %s
            """
            params = [job_id]  # Initialize with the creator ID

            # Conditionally add filters
            if job_title:
                query += " AND j.title = %s"  # Add job title filter
                params.append(job_title)

            if status:
                query += " AND a.status = %s"  # Add application status filter
                params.append(status)

            # Execute the final query
            cursor.execute(query, params)
            applications = cursor.fetchall()
            return applications  # Return results as a list of dictionaries
        except mysql.connector.Error as err:
            raise Exception(f"Error fetching applications by job ID: {err}")
        finally:
            cursor.close()
    # def update_status(self, application_id, status):
    #     cursor = self.db_connection.cursor()
    #     try:
    #         cursor.execute("""
    #             UPDATE Applications
    #             SET status = %s, updated_at = CURRENT_TIMESTAMP
    #             WHERE id = %s
    #         """, (status, application_id))

    #         self.db_connection.commit()

    #         # Check if any row was affected
    #         return cursor.rowcount > 0  # True if the application was found and updated
    #     except mysql.connector.Error as err:
    #         self.db_connection.rollback()
    #         raise Exception(f"Error updating application status: {err}")
    #     finally:
    #         cursor.close()
            
    def update_status(self, application_id, status):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("""
                UPDATE Applications
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (status, application_id))

            self.db_connection.commit()
            return cursor.rowcount > 0  # Return True if the application was found and updated
        except mysql.connector.Error as err:
            self.db_connection.rollback()
            raise Exception(f"Error updating application status: {err}")
        finally:
            cursor.close()

    def fetch_applications_by_creator(self, created_by, job_title=None, status=None):
        cursor = self.db_connection.cursor(dictionary=True)  # Use dictionary cursor for easy conversion
        try:
            # Construct the base query
            query = """
                SELECT a.id AS application_id,
                       a.job_id,
                       a.first_name,
                       a.last_name,
                       a.email,
                       a.phone_number,
                       a.experience,
                       a.current_ctc,
                       a.expected_ctc,
                       a.resume,
                       a.status AS application_status,
                       a.submitted_at,
                       a.updated_at,
                       a.openai_score,
                       a.nlp_score,
                       j.title AS job_title,
                       j.description AS job_description,
                       j.department AS job_department,
                       j.experience AS job_experience,
                       j.location AS job_location,
                       j.employment_type AS job_employment_type,
                       j.salary_range AS job_salary_range,
                       j.status AS job_status
                FROM Applications a
                JOIN Jobs j ON a.job_id = j.job_id
                WHERE j.created_by = %s
            """
            params = [created_by]  # Initialize with the creator ID

            # Conditionally add filters
            if job_title:
                query += " AND j.title = %s"  # Add job title filter
                params.append(job_title)

            if status:
                query += " AND a.status = %s"  # Add application status filter
                params.append(status)

            # Execute the final query
            cursor.execute(query, params)
            applications = cursor.fetchall()
            return applications  # Return results as a list of dictionaries
        except mysql.connector.Error as err:
            raise Exception(f"Error fetching applications by creator: {err}")
        finally:
            cursor.close()
            
    def fetch_applications_by_candiadteId(self, candidate_id, job_title=None, status=None):
        cursor = self.db_connection.cursor(dictionary=True)  # Use dictionary cursor for easy conversion
        try:
            # Construct the base query
            query = """
                SELECT a.id AS application_id,
                       a.job_id,
                       a.first_name,
                       a.last_name,
                       a.email,
                       a.phone_number,
                       a.experience,
                       a.current_ctc,
                       a.expected_ctc,
                       a.resume,
                       a.status AS application_status,
                       a.submitted_at,
                       a.updated_at,
                       a.openai_score,
                       a.nlp_score,
                       j.title AS job_title,
                       j.description AS job_description,
                       j.department AS job_department,
                       j.experience AS job_experience,
                       j.location AS job_location,
                       j.employment_type AS job_employment_type,
                       j.salary_range AS job_salary_range,
                       j.status AS job_status
                FROM Applications a
                JOIN Jobs j ON a.job_id = j.job_id
                WHERE a.candidate_id = %s
            """
            params = [candidate_id]  # Initialize with the cadidate ID

            # Conditionally add filters
            if job_title:
                query += " AND j.title = %s"  # Add job title filter
                params.append(job_title)

            if status:
                query += " AND a.status = %s"  # Add application status filter
                params.append(status)

            # Execute the final query
            cursor.execute(query, params)
            applications = cursor.fetchall()
            return applications  # Return results as a list of dictionaries
        except mysql.connector.Error as err:
            raise Exception(f"Error fetching applications by creator: {err}")
        finally:
            cursor.close()
            
    def get_resume_path_by_application_id(self, application_id):
        try:
            self.cursor.execute("SELECT resume FROM Applications WHERE id = %s", (application_id,))
            resume_path = self.cursor.fetchone()
            if resume_path:
                return resume_path['resume'] if resume_path['resume'] else None
            return None
        except Exception as e:
            print("Error fetching resume path:", str(e))
            return None
        finally:
            self.cursor.close()  # Close cursor here, if applicable
            
    def get_job_description_by_job_id(self, job_id):
        cursor = self.db_connection.cursor(dictionary=True)  # Use dictionary for easy access to results
        try:
            self.cursor.execute("SELECT description FROM Jobs WHERE job_id = %s", (job_id,))
            job = self.cursor.fetchone()
            
            if not job:
                raise Exception("Job not found.")

            job_description = job['description']
            return job_description
        except mysql.connector.Error as err:
            raise Exception(f"Error fetching job logs: {err}")
        finally:
            cursor.close() 
