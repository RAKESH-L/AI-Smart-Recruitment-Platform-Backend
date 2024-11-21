from flask import Blueprint, request, jsonify
from app.service.linkedin_service import LinkedInService

linkedin_bp = Blueprint('linkedin', __name__)

@linkedin_bp.route('/post', methods=['POST'])
def post_job():
    data = request.json
    job_title = data.get('job_title')
    job_description = data.get('job_description')
    job_location = data.get('job_location')
    skills = data.get('skills', [])

    linkedin_service = LinkedInService()
    success = linkedin_service.post_job(job_title, job_description, job_location, skills)

    if success:
        return jsonify({'message': 'Job posted successfully'}), 200
    else:
        return jsonify({'message': 'Failed to post job'}), 500
