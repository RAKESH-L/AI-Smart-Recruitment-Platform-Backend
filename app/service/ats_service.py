import mysql.connector
import requests
import json
import os
import spacy
from PyPDF2 import PdfReader
from docx import Document
from config import MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE_NAME
from app.service.openai_service import call_openai_api

class ATSService:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.db = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE_NAME
        )
        self.cursor = self.db.cursor(dictionary=True)

    def fetch_and_rank_applications(self, job_id):
        # Fetch job requirements based on the job ID
        self.cursor.execute("SELECT description FROM Jobs WHERE job_id = %s", (job_id,))
        job = self.cursor.fetchone()
        
        if not job:
            raise Exception("Job not found.")

        job_description = job['description']
        
        # Fetch applications for the given job ID, include resume path
        self.cursor.execute("""
            SELECT 
                a.id,
                a.first_name,
                a.last_name,
                a.email,
                a.resume,
                a.experience,
                a.status
            FROM Applications a
            WHERE a.job_id = %s
        """, (job_id,))
        
        applications = self.cursor.fetchall()

        for application in applications:
            resume_content = self.read_resume(application['resume'])
            application['similarity_score'] = self.evaluate_candidate(job_description, resume_content)

        # Sort by similarity score (descending)
        applications.sort(key=lambda x: x['similarity_score'], reverse=True)

        return applications

    def read_resume(self, resume_path):
        """ Read the content of a resume based on its file type. """
        if not os.path.exists(resume_path):
            return ""

        if resume_path.lower().endswith('.pdf'):
            reader = PdfReader(resume_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        elif resume_path.lower().endswith('.docx'):
            doc = Document(resume_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text.strip()
        else:
            raise Exception("Unsupported file type for resume.")

    def evaluate_candidate(self, job_description, resume_content):
    # Use OpenAI model to evaluate the resume against the job description
        prompt = (
            f"Given the following job description:\n\n{job_description}\n\n"
            f"Evaluate the following resume content and provide a only give numeric similarity score from 1 to 100 not like 73 out of 100 or 36 out of 100 only one number:\n\n{resume_content}"
        )

        response_text = call_openai_api(prompt)
        print(f"Response from OpenAI: '{response_text}'")  # Debug output

        try:
            similarity_score = float(response_text)
            return similarity_score
        except ValueError:
            print(f"Failed to convert response to a float. Response was: '{response_text}'")
            return 0  # Return 0 if the score cannot be interpreted


    def close_connection(self):
        self.cursor.close()
        self.db.close()

    def fetch_and_rank_applicationsNLP(self, job_id):
        self.cursor.execute("SELECT description FROM Jobs WHERE job_id = %s", (job_id,))
        job = self.cursor.fetchone()
        
        if not job:
            raise Exception("Job not found.")

        job_description = job['description']
        
        # Fetch applications for the given job ID, include resume path
        self.cursor.execute("""
            SELECT 
                a.id,
                a.first_name,
                a.last_name,
                a.email,
                a.resume,
                a.experience,
                a.status
            FROM Applications a
            WHERE a.job_id = %s
        """, (job_id,))
        
        applications = self.cursor.fetchall()

        for application in applications:
            resume_content = self.read_resume(application['resume'])
            application['similarity_score'] = self.calculate_similarity(job_description, resume_content)

        applications.sort(key=lambda x: x['similarity_score'], reverse=True)

        return applications
    
    def calculate_similarity(self, job_description, candidate_resume):
        doc_job = self.nlp(job_description)
        doc_resume = self.nlp(candidate_resume)
        similarity_score = doc_job.similarity(doc_resume)
        return similarity_score