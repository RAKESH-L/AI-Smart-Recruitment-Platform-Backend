import os
from flask import Blueprint, request, jsonify
from app.service.application_service import ApplicationService
from app.service.ats_service import ATSService
from flask import send_file, jsonify
import io

application_controller = Blueprint('application_controller', __name__)
application_service = ApplicationService()
ats_service = ATSService()

@application_controller.route('/postApplication', methods=['POST'])
def create_application():
    """ Post details for applications """

    # Define path to save resumes
    resume_upload_path = 'C:\\Users\\2000080631\\workspace\\Designathon 2024 - 2.0\\Candidates Resume'

    # print("data", request.form)
    # print("file", request.files)
    # Check if the request contains required fields and the file
    if 'resume' not in request.files or 'job_id' not in request.form:
        return jsonify({'message': 'Missing required fields or resume file.'}), 400

    resume_file = request.files['resume']
    job_id = request.form['job_id']
    phone_number = request.form.get('phone_number')
    first_name = request.form.get('first_name')
    skills = request.form.getlist('skills')  # Assuming skills can come as a list

    # Ensure the file has an acceptable type and format the file name
    if resume_file and resume_file.filename.lower().endswith(('.pdf', '.docx')):
        # Construct the new filename based on jobId and phoneNumber
        resume_filename = f"{job_id}_{phone_number}_{first_name}.pdf"  # Change to .docx if needed
        resume_filepath = os.path.join(resume_upload_path, resume_filename)

        # Check if the application already exists
        exists = application_service.check_existing_application(job_id, phone_number)
        if exists:
            return jsonify({'message': 'Application already exists for this job and phone number.'}), 400
        
        # Save the resume
        resume_file.save(resume_filepath)
    else:
        return jsonify({'message': 'Invalid file type. Only .pdf and .docx are allowed.'}), 400

    resume_content = ats_service.read_resume(resume_filepath)
    
     # Get job description from the database
    job_description = application_service.get_job_description_by_job_id(job_id)

    # Calculate the OpenAI score and NLP score
    openai_score = ats_service.evaluate_candidate(job_description, resume_content)
    nlp_score = ats_service.calculate_similarity(job_description, resume_content)

    # Prepare application data
    application_data = {
        'job_id': job_id,
        'first_name': first_name,
        'last_name': request.form.get('last_name'),
        'email': request.form.get('email'),
        'phone_number': phone_number,
        'experience': request.form.get('experience'),
        'current_ctc': request.form.get('current_ctc'),
        'expected_ctc': request.form.get('expected_ctc'),
        'resume': resume_filepath,  # Use the saved path
        'status': 'submitted',  # You can set a default status here
        'candidate_id': request.form.get('candidate_id'),
        'offer_accepted_date': request.form.get('offer_accepted_date'),
        'openai_score': openai_score,  # Assign calculated OpenAI score
        'nlp_score': nlp_score           # Assign calculated NLP score
    }

    try:
        # Create the application and save the application ID
        application_id = application_service.create_application(application_data, skills)
        return jsonify({'message': 'Application and Skills created successfully!', 'application_id': application_id}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@application_controller.route('/getApplicationsByjobId/<int:job_id>', methods=['GET'])
def get_applications_by_job_id(job_id):
    """ Get applications for a specific job ID """
    job_title = request.args.get('job_title')  # Optional
    status = request.args.get('status')  # Optional

    try:
        applications = application_service.get_applications_by_job_id(job_id, job_title, status)
        if not applications:
            return jsonify({'message': 'No applications found for this job ID.'}), 404
        
        return jsonify(applications), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@application_controller.route('/updateStatusByApplicationId/<int:application_id>/status', methods=['PUT'])
def update_application_status(application_id):
    """ Update the status of an application based on application ID """
    
    data = request.get_json()
    
    # Validate the input
    if not data or 'status' not in data:
        return jsonify({'message': 'Status is required.'}), 400

    status = data['status']

    try:
        # Update the application status
        success = application_service.update_application_status(application_id, status)
        
        if success:
            return jsonify({'message': 'Application status updated successfully!'}), 200
        else:
            return jsonify({'message': 'Application not found.'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@application_controller.route('/acceptOffer', methods=['POST'])
def accept_offer():
    data = request.get_json()

    # Validate incoming data
    application_id = data.get("application_id")
    offer_accepted_date = data.get("offer_accepted_date")  # Expecting a date string from the request

    if not application_id or not offer_accepted_date:
        return jsonify({"message": "Missing application_id or offer_accepted_date"}), 400

    try:
        # Call the service method to accept the offer
        updated = application_service.accept_offer(application_id, offer_accepted_date)

        if updated:
            return jsonify({"message": "Offer accepted successfully!"}), 200
        else:
            return jsonify({"message": "Application status is not 'offered'."}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    
@application_controller.route('/applicationsBycreatedBy/<string:created_by>', methods=['GET'])
def get_applications_by_creator(created_by):
    """Fetch applications created by a specific user (creator). Optionally filter by job title and application status."""
    job_title = request.args.get('job_title')  # Optional
    status = request.args.get('status')  # Optional

    try:
        applications = application_service.get_applications_by_creator(created_by, job_title, status)
        if applications:
            response = jsonify(applications)
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            return response, 200 
        else:
            return jsonify({'message': 'No applications found for this creator.'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@application_controller.route('/getResumeByApplicationId/<int:application_id>', methods=['GET'])
def get_resume(application_id):
    resume_content, status_code = application_service.get_resume_by_application_id(application_id)

    if status_code == 200:
        return send_file(
            io.BytesIO(resume_content),
            mimetype='application/pdf',  # Change the mimetype according to your file type
            as_attachment=True,
            download_name='resume.pdf'  # Provide a name for the downloaded file
        )
    else:
        return jsonify(resume_content), status_code@application_controller.route('/applicationsBycreatedBy/<string:created_by>', methods=['GET'])

@application_controller.route('/applicationsByCandidateId/<string:candidate_id>', methods=['GET'])
def get_applications_by_candidateId(candidate_id):
    """Fetch applications created by a specific user (creator). Optionally filter by job title and application status."""
    job_title = request.args.get('job_title')  # Optional
    status = request.args.get('status')  # Optional

    try:
        applications = application_service.get_applications_by_candidateId(candidate_id, job_title, status)
        if applications:
            return jsonify(applications), 200  # Respond with a list of applications
        else:
            return jsonify({'message': 'No applications found for this creator.'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
