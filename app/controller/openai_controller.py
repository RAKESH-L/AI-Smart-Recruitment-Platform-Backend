from flask import Blueprint, jsonify, request
from app.service.openai_service import generate_response_text

openai_controller = Blueprint('openai_controller', __name__)
# openai_service = OpenAIService()

@openai_controller.route('/generateJD', methods=['POST'])
def generate_job_description():
    """ Endpoint to generate job description. """
    data = request.get_json()
    
    job_title = data.get('job_title')
    experience = data.get('experience')
    location = data.get('location', '')  # Defaults to empty string if not provided
    employment_type = data.get('employment_type')
    salary_range = data.get('salary_range')
    company_name = data.get('company_name')
    # skills = data.get('skills', [])  

    # Validate input
    if not job_title or not experience or not employment_type or not salary_range or not company_name :
        return jsonify({"error": "Please provide job_title, experience, employment_type, salary_range, company_name, and skills."}), 400
    
    try:
        prompt = (
            f"Generate a detailed job description for the following position:\n\n"
            f"**Job Title**: {job_title}\n\n"
            f"**Experience Required**: {experience} years\n\n"
            f"**Location**: {location} (optional)\n\n"
            f"**Employment Type**: {employment_type}\n\n"
            f"**Salary Range**: {salary_range}\n\n"
            f"**Company Name**: {company_name}\n\n"
            f"Use the information above to outline responsibilities, qualifications, and any other relevant details, "
            f"including a summary of the company if necessary."
        )
        job_description = generate_response_text(prompt)
        print(job_description)
        return jsonify({"job_description": job_description}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500