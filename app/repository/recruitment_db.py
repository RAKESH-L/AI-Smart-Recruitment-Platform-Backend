import mysql.connector
import os
from config import MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE_NAME
 
class DatabaseService:
    def __init__(self):
        try:
            # Connect to MySQL server
            self.db = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USERNAME,
                password=MYSQL_PASSWORD
            )
            self.cursor = self.db.cursor()
 
            # Create database if it doesn't exist
            self.create_database()
 
            # Connect to the created database
            self.db.database = MYSQL_DATABASE_NAME
 
            # Create tables
            self.create_tables()
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")
            self.db = None
            self.cursor = None
 
    def create_database(self):
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE_NAME}")
        print(f"Database `{MYSQL_DATABASE_NAME}` is ready.")
 
    def create_tables(self):
        # User table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                employee_id VARCHAR(255) PRIMARY KEY,
                full_name VARCHAR(255),
                username VARCHAR(255) UNIQUE,
                phone_number VARCHAR(20),
                password VARCHAR(255),
                role ENUM('admin', 'recruiter', 'interviewer', 'candidate'),
                email VARCHAR(255) UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)

 
        # Jobs table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Jobs (
                job_id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255),
                description TEXT,
                department VARCHAR(255),
                experience VARCHAR(255),
                location VARCHAR(255),
                employment_type ENUM('full-time', 'part-time', 'contract'),
                salary_range VARCHAR(255),
                status ENUM('open', 'closed', 'in progress', 'drafted', 'deleted'),
                client VARCHAR(255),
                application_deadline DATE,
                created_by VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES Users(employee_id)
            )
        """)
 
        # Candidates table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Candidates (
                candidate_id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                email VARCHAR(255) UNIQUE,
                phone_number VARCHAR(20),
                experience VARCHAR(255),
                resume VARCHAR(255),
                status ENUM('applied', 'interviewing', 'hired', 'rejected'),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
 
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Applications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_id INT,
                candidate_id VARCHAR(255),
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                email VARCHAR(255) UNIQUE,
                phone_number VARCHAR(20),
                experience VARCHAR(255),
                current_ctc DECIMAL(10, 2),
                expected_ctc DECIMAL(10, 2),
                resume VARCHAR(255),
                status ENUM('submitted', 'shortlisted', 'interviewing', 'offered', 'accepted', 'rejected', 'hired'),
                offer_accepted_date TIMESTAMP NULL DEFAULT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                openai_score DECIMAL(5, 2) DEFAULT NULL,  -- New field
                nlp_score DECIMAL(5, 2) DEFAULT NULL,      -- New field
                FOREIGN KEY (job_id) REFERENCES Jobs(job_id),
                FOREIGN KEY (candidate_id) REFERENCES Users(employee_id)
            )
        """)
 
        # Interviews table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Interviews (
                interview_id INT AUTO_INCREMENT PRIMARY KEY,
                type ENUM('HR interview', 'Technical interview', 'Managerial interview'),
                job_id INT,
                interviewer_id VARCHAR(255),
                application_id INT,
                owner_id VARCHAR(255),
                schedule_date DATETIME,
                status ENUM('scheduled', 'completed', 'cancelled'),
                feedback TEXT,
                interviewMode ENUM('remote', 'in-person', 'video-call', 'phone-call', 'teams-call') DEFAULT 'remote',  -- New field for interview mode
                interviewLocation VARCHAR(255) DEFAULT 'online',  -- New field for interview location with default value
                FOREIGN KEY (job_id) REFERENCES Jobs(job_id),
                FOREIGN KEY (interviewer_id) REFERENCES Users(employee_id),
                FOREIGN KEY (application_id) REFERENCES Applications(id),
                FOREIGN KEY (owner_id) REFERENCES Users(employee_id)
            )
        """)

 
        # Performance Analytics table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS PerformanceAnalytics (
                performance_id INT AUTO_INCREMENT PRIMARY KEY,
                job_id INT,
                metric_name VARCHAR(255),
                metric_value VARCHAR(255),
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES Jobs(job_id)
            )
        """)
 
        # Job Posting Log table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS JobPostingLog (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                job_id INT,
                action ENUM('created', 'updated', 'closed'),
                performed_by VARCHAR(255),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES Jobs(job_id),
                FOREIGN KEY (performed_by) REFERENCES Users(employee_id)
            )
        """)
 
        # Job Skills table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS JobSkills (
                skill_id INT AUTO_INCREMENT PRIMARY KEY,
                job_id INT,
                skill_name VARCHAR(255),
                FOREIGN KEY (job_id) REFERENCES Jobs(job_id)
            )
        """)
 
        # Candidate Skills table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS CandidateSkills (
                skill_id INT AUTO_INCREMENT PRIMARY KEY,
                application_id INT,
                skill_name VARCHAR(255),
                FOREIGN KEY (application_id) REFERENCES Applications(id)
            )
        """)
 
        print("Tables created successfully.")
 