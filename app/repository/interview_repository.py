import mysql.connector
import json

class InterviewRepository:
    
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def insert_interview(self, interview_data):
        cursor = self.db_connection.cursor()

        try:
            # Check if feedback exists
            feedback = interview_data.get('feedback')
            
            if feedback is None or feedback == "":  # If feedback is not provided or is an empty string
                feedback = None  # Set it to None for SQL to insert a NULL value
            else:
                feedback = json.dumps(feedback)  # Serialize to JSON string if feedback is present

            cursor.execute("""
                INSERT INTO Interviews (type, job_id, interviewer_id, application_id, owner_id,
                                        schedule_date, status, feedback, interviewMode, interviewLocation)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                interview_data['type'],
                interview_data['job_id'],
                interview_data['interviewer_id'],
                interview_data['application_id'],
                interview_data['owner_id'],
                interview_data['schedule_date'],
                interview_data['status'],
                feedback,  # This will be NULL if no feedback is provided
                interview_data.get('interviewMode'),  # Fetch interviewMode safely
                interview_data.get('interviewLocation')  # Fetch interviewLocation safely
            ))

            self.db_connection.commit()
            return cursor.lastrowid  # Return the ID of the newly inserted interview
        except mysql.connector.Error as err:
            self.db_connection.rollback()
            raise Exception(f"Error inserting interview: {err}")
        finally:
            cursor.close()
            
    def check_existing_scheduled_interview(self, application_id, job_id, interview_type):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM Interviews
                WHERE application_id = %s AND job_id = %s AND type = %s AND status = 'scheduled'
            """, (application_id, job_id, interview_type))
            count = cursor.fetchone()[0]
            return count > 0  # Return True if a scheduled interview exists
        except mysql.connector.Error as err:
            raise Exception(f"Error checking existing scheduled interview: {err}")
        finally:
            cursor.close()
            
    def update_interview(self, interview_id, interview_data):
        cursor = self.db_connection.cursor()
        try:
            sql = "UPDATE Interviews SET "
            update_fields = []
            values = []

            # Dynamically build the SET clause based on the provided fields
            for key in interview_data:
                if key in ['type', 'job_id', 'interviewer_id', 'application_id', 'owner_id', 'schedule_date', 'status']:
                    update_fields.append(f"{key} = %s")
                    values.append(interview_data[key])
                elif key == 'feedback':
                    # Convert feedback dictionary to JSON string
                    feedback_json = json.dumps(interview_data[key])  # Serialize to JSON
                    update_fields.append("feedback = %s")
                    values.append(feedback_json)

            # Ensure the interview ID is included in the values for the WHERE clause
            values.append(interview_id)

            # If no fields are provided for update, raise an error
            if not update_fields:
                raise ValueError("No valid fields provided for update.")

            sql += ", ".join(update_fields)  # Join the fields with commas
            sql += " WHERE interview_id = %s"

            cursor.execute(sql, values)  # Pass the values to be safely substituted in the SQL statement
            self.db_connection.commit()
            return cursor.rowcount > 0  # Return True if the interview was found and updated
        except mysql.connector.Error as err:
            self.db_connection.rollback()
            raise Exception(f"Error updating interview: {err}")
        except ValueError as ve:
            return False  # If there are no valid fields, respond accordingly
        finally:
            cursor.close()
            
    def fetch_interviews_by_interviewer(self, interviewer_id):
        cursor = self.db_connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    i.*,
                    j.title AS job_title,
                    j.description AS job_description,
                    j.department AS job_department,
                    j.location AS job_location,
                    a.first_name AS applicant_first_name,
                    a.last_name AS applicant_last_name,
                    a.email AS applicant_email,
                    a.phone_number AS applicant_phone,
                    u_full.full_name AS interviewer_full_name,
                    u_full.username AS interviewer_username,
                    u_full.email AS interviewer_email,
                    u_owner.full_name AS owner_full_name,
                    u_owner.username AS owner_username,
                    u_owner.email AS owner_email
                FROM Interviews i
                JOIN Jobs j ON i.job_id = j.job_id
                JOIN Applications a ON i.application_id = a.id
                JOIN Users u_full ON i.interviewer_id = u_full.employee_id  -- For Interviewer details
                JOIN Users u_owner ON i.owner_id = u_owner.employee_id    -- For Owner details
                WHERE interviewer_id = %s
            """, (interviewer_id,))
            return cursor.fetchall()  # Fetch all interviews for the given interviewer
        except mysql.connector.Error as err:
            raise Exception(f"Error fetching interviews: {err}")
        finally:
            cursor.close()
            
    def fetch_interviews_by_owner(self, owner_id):
        cursor = self.db_connection.cursor(dictionary=True)  # Use dictionary cursor for easy manipulation
        try:
            cursor.execute("""
                SELECT 
                    i.*,
                    j.title AS job_title,
                    j.description AS job_description,
                    j.department AS job_department,
                    j.location AS job_location,
                    a.first_name AS applicant_first_name,
                    a.last_name AS applicant_last_name,
                    a.email AS applicant_email,
                    a.phone_number AS applicant_phone,
                    u_full.full_name AS interviewer_full_name,
                    u_full.username AS interviewer_username,
                    u_full.email AS interviewer_email,
                    u_owner.full_name AS owner_full_name,
                    u_owner.username AS owner_username,
                    u_owner.email AS owner_email
                FROM Interviews i
                JOIN Jobs j ON i.job_id = j.job_id
                JOIN Applications a ON i.application_id = a.id
                JOIN Users u_full ON i.interviewer_id = u_full.employee_id  -- For Interviewer details
                JOIN Users u_owner ON i.owner_id = u_owner.employee_id    -- For Owner details
                WHERE i.owner_id = %s
            """, (owner_id,))
            return cursor.fetchall()  # Fetch all interviews for the given owner
        except mysql.connector.Error as err:
            raise Exception(f"Error fetching interviews: {err}")
        finally:
            cursor.close()
            
    def fetch_interviews_by_application(self, application_id):
        cursor = self.db_connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT * FROM Interviews
                WHERE application_id = %s
            """, (application_id,))
            return cursor.fetchall()  # Fetch all interviews for the given application
        except mysql.connector.Error as err:
            raise Exception(f"Error fetching interviews: {err}")
        finally:
            cursor.close()

    def fetch_interviews_by_job_and_owner(self, job_id, owner_id):
        cursor = self.db_connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT * FROM Interviews
                WHERE job_id = %s AND owner_id = %s
            """, (job_id, owner_id))
            return cursor.fetchall()  # Fetch all interviews for the given job and owner
        except mysql.connector.Error as err:
            raise Exception(f"Error fetching interviews: {err}")
        finally:
            cursor.close()
            
    def fetch_interviews_by_job_and_interview(self, job_id, interviewer_id):
        cursor = self.db_connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT * FROM Interviews
                WHERE job_id = %s AND interviewer_id = %s
            """, (job_id, interviewer_id))
            return cursor.fetchall()  # Fetch the interview for the given job and interview ID
        except mysql.connector.Error as err:
            raise Exception(f"Error fetching interviews: {err}")
        finally:
            cursor.close()