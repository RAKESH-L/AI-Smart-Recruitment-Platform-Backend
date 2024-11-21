import os
from flask import Blueprint, request, jsonify
from app.service.candidate_service import CandidateService

candidate_controller = Blueprint('candidate_controller', __name__)
candidate_service = CandidateService()

@candidate_controller.route('/postCandidates', methods=['POST'])
def create_candidate():
    """ Post details for candidates and their skills """
    # Define path to save resumes
    resume_upload_path = 'C:\\Users\\2000080631\\workspace\\Designathon 2024 - 2.0\\Candidates Resume'

    # Check if the request contains the file and candidate details
    if 'resume' not in request.files or 'first_name' not in request.form or 'last_name' not in request.form:
        return jsonify({'message': 'Missing required fields or resume file.'}), 400
      
    resume_file = request.files['resume']
    
    # Ensure the file is of an acceptable type (e.g., PDF or DOCX)
    if resume_file and resume_file.filename.lower().endswith(('.pdf', '.docx')):
        # Save the resume
        resume_filename = resume_file.filename
        resume_filepath = os.path.join(resume_upload_path, resume_filename)
        resume_file.save(resume_filepath)
    else:
        return jsonify({'message': 'Invalid file type. Only .pdf and .docx are allowed.'}), 400

    # Prepare candidate data
    candidate_data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form.get('email'),
        'phone_number': request.form.get('phone_number'),
        'experience': request.form.get('experience'),
        'resume': resume_filepath,  # Use the saved path
        'skills': request.form.getlist('skills')  # Assume skills can come as a list
    }

    try:
        # Create the candidate and their skills
        candidate_id = candidate_service.create_candidate(candidate_data)
        return jsonify({'message': 'Candidate created successfully!', 'candidate_id': candidate_id}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500
