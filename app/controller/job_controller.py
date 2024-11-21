from flask import Blueprint, request, jsonify
from app.service.job_service import JobService
import bcrypt

job_controller = Blueprint('job_controller', __name__)
job_service = JobService()

@job_controller.route('/postJobsWithSkills', methods=['POST'])
def create_job():
    data = request.get_json()

    if not data or 'title' not in data or 'description' not in data:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        # Create the job and only insert job details initially
        job_id = job_service.create_job(data)
        
        # Log the job creation action
        job_service.log_job_action(job_id, 'created', data.get('created_by'))  # Assumes 'created_by' is passed in the request
        
        # Insert job skills if provided
        if 'skills' in data:
            # Assuming skills is a list of skill names
            job_service.add_job_skills(job_id, data['skills'])

        return jsonify({'job_id': job_id, 'message': 'Job created successfully!'}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@job_controller.route('/getJobsByEmployeeId/<string:created_by>', methods=['GET'])
def get_jobs_by_creator(created_by):
    """ Fetch all jobs created by a specific user and filter by status """

    # Get the 'status' query parameter (optional)
    status = request.args.get('status')

    try:
        jobs = job_service.get_jobs_by_creator(created_by, status)

        if jobs:
            return jsonify(jobs), 200
        else:
            return jsonify({'message': 'No jobs found for this creator.'}), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500

    
@job_controller.route('/updateJobDetailsByJobId/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    """ Update job details and skills based on job_id """
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided for update.'}), 400

    try:
        job = job_service.get_job_by_id(job_id)  # Ensure you have a method to fetch job details for getting the 'created_by'

        updated_job = job_service.update_job(job_id, data)
        
        # Log the job update action
        job_service.log_job_action(job_id, 'updated', job['created_by'])  # Assumes 'updated_by' is passed in the request

        if 'skills' in data:
            # Update job skills if provided in the request
            job_service.update_job_skills(job_id, data['skills'])

        return jsonify({'message': 'Job updated successfully!', 'job_id': job_id}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@job_controller.route('/deleteJobByJobId/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    """ Delete job and its associated job skills based on job_id """
    try:
        job = job_service.get_job_by_id(job_id)  # Ensure you have a method to fetch job details for getting the 'created_by'
        
        job_service.delete_job(job_id)
        
        # Log the job deletion action
        job_service.log_job_action(job_id, 'closed', job['created_by'])  # Use the retrieved job details for 'created_by'

        return jsonify({'message': 'Job and associated skills deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@job_controller.route('/getJobPostingLogs', methods=['GET'])
def get_job_posting_logs():
    """ Fetch all job posting logs """
    try:
        logs = job_service.get_job_posting_logs()  # Call the service method
        return jsonify(logs), 200  # Return logs as JSON
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@job_controller.route('/getjobLogsByAction/<string:action>', methods=['GET'])
def get_job_posting_logs_by_action(action):
    """ Fetch job posting logs filtered by action """
    try:
        logs = job_service.get_job_posting_logs_by_action(action)  # Call the service method
        if logs:
            return jsonify(logs), 200  # Return logs as JSON
        else:
            return jsonify({'message': 'No logs found for this action.'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
