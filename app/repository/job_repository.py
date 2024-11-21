import mysql.connector
from config import MYSQL_DATABASE_NAME

class JobRepository:
    
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def insert_job(self, job_data):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO Jobs (title, description, department, experience, location, employment_type,  salary_range, status, client, application_deadline, created_by) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                job_data['title'],
                job_data['description'],
                job_data.get('department'),  # Use .get() to provide a default if key doesn't exist
                job_data.get('experience'),
                job_data.get('location'),
                job_data.get('employment_type'),
                job_data.get('salary_range'),
                job_data.get('status', 'open'),  # Default status if not provided
                job_data.get('client'),
                job_data.get('application_deadline'),
                job_data.get('created_by')  # Assume created_by is passed in if available
            ))
            self.db_connection.commit()
            return cursor.lastrowid  # Return the ID of the newly inserted job
        except mysql.connector.Error as err:
            self.db_connection.rollback()
            raise Exception(f"Error inserting job: {err}")
        finally:
            cursor.close()

    def insert_job_skills(self, job_id, skills):
        cursor = self.db_connection.cursor()
        try:
            for skill in skills:
                cursor.execute("""
                    INSERT INTO JobSkills (job_id, skill_name) 
                    VALUES (%s, %s)
                """, (job_id, skill))

            self.db_connection.commit()  # Commit after inserting all skills
        except mysql.connector.Error as err:
            self.db_connection.rollback()
            raise Exception(f"Error inserting job skills: {err}")
        finally:
            cursor.close()
            
    def fetch_jobs_by_creator(self, created_by, status=None):
        cursor = self.db_connection.cursor(dictionary=True)  # Use dictionary cursor for easy JSON conversion

        try:
            # SQL query to fetch jobs and associated skills
            query = """
                SELECT j.job_id, j.title, j.description, j.department, j.experience,
                    j.location, j.employment_type, j.salary_range, j.status, j.client, j.application_deadline,
                    j.created_at, j.updated_at,
                    GROUP_CONCAT(js.skill_name) AS skills
                FROM Jobs j
                LEFT JOIN JobSkills js ON js.job_id = j.job_id
                WHERE j.created_by = %s
            """
            
            params = [created_by]

            # If status is provided, add to the WHERE clause
            if status:
                # Split statuses by comma and sanitize input
                status_list = status.split(',')
                placeholders = ', '.join(['%s'] * len(status_list))  # Create a string of placeholders
                query += f" AND j.status IN ({placeholders})"
                params.extend(status_list)  # Add statuses to the parameters

            query += " GROUP BY j.job_id"

            # Execute the query with parameters
            cursor.execute(query, params)
            jobs = cursor.fetchall()

            return jobs  # Return fetched job details with skills

        except mysql.connector.Error as err:
            raise Exception(f"Error fetching jobs by creator: {err}")
        finally:
            cursor.close()

            
    def update_job(self, job_id, job_data):
        cursor = self.db_connection.cursor()
        try:
            # Prepare SQL update statement
            sql_update_query = """
                UPDATE Jobs
                SET title = %s, description = %s, department = %s, 
                    experience = %s, location = %s, 
                    employment_type = %s, salary_range = %s, 
                    status = %s, client = %s, application_deadline = %s, updated_at = CURRENT_TIMESTAMP
                WHERE job_id = %s
            """
            cursor.execute(sql_update_query, (
                job_data.get('title'),
                job_data.get('description'),
                job_data.get('department'),
                job_data.get('experience'),
                job_data.get('location'),
                job_data.get('employment_type'),
                job_data.get('salary_range'),
                job_data.get('status'),
                job_data.get('client'),
                job_data.get('application_deadline'),
                job_id
            ))
            self.db_connection.commit()

            if cursor.rowcount == 0:
                raise Exception("No job found with the given ID.")

        except mysql.connector.Error as err:
            self.db_connection.rollback()
            raise Exception(f"Error updating job: {err}")
        finally:
            cursor.close()

    def update_job_skills(self, job_id, skills):
        cursor = self.db_connection.cursor()
        try:
            # First, clear existing skills for the job
            cursor.execute("DELETE FROM JobSkills WHERE job_id = %s", (job_id,))

            # Now, insert new skills
            for skill in skills:
                cursor.execute("""
                    INSERT INTO JobSkills (job_id, skill_name) 
                    VALUES (%s, %s)
                """, (job_id, skill))

            self.db_connection.commit()  # Commit after inserting all skills

        except mysql.connector.Error as err:
            self.db_connection.rollback()
            raise Exception(f"Error updating job skills: {err}")
        finally:
            cursor.close()
            
    def delete_job(self, job_id):
        cursor = self.db_connection.cursor()
        try:
            # Delete associated job skills first
            cursor.execute("DELETE FROM JobSkills WHERE job_id = %s", (job_id,))
            # Now, delete the job
            cursor.execute("DELETE FROM Jobs WHERE job_id = %s", (job_id,))
            self.db_connection.commit()

            if cursor.rowcount == 0:
                raise Exception("No job found with the given ID.")
        
        except mysql.connector.Error as err:
            self.db_connection.rollback()
            raise Exception(f"Error deleting job: {err}")
        finally:
            cursor.close()
    
    def fetch_job_posting_logs(self):
        cursor = self.db_connection.cursor(dictionary=True)  # Using dictionary cursor for easy JSON conversion
        try:
            cursor.execute("""
                SELECT log_id, job_id, action, performed_by, timestamp
                FROM JobPostingLog
                ORDER BY timestamp DESC
            """)  # Fetch all log details, ordered by timestamp
            logs = cursor.fetchall()
            return logs  # Return fetched logs as a list of dictionaries
        except mysql.connector.Error as err:
            raise Exception(f"Error fetching job posting logs: {err}")
        finally:
            cursor.close()
            
    def fetch_job_posting_logs_by_action(self, action):
        cursor = self.db_connection.cursor(dictionary=True)  # Using dictionary cursor for easy JSON conversion
        try:
            cursor.execute("""
                SELECT log_id, job_id, action, performed_by, timestamp
                FROM JobPostingLog
                WHERE action = %s
                ORDER BY timestamp DESC
            """, (action,))  # Filter logs by action
            logs = cursor.fetchall()
            return logs  # Return fetched logs as a list of dictionaries
        except mysql.connector.Error as err:
            raise Exception(f"Error fetching job posting logs by action: {err}")
        finally:
            cursor.close()
            
    