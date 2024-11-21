from flask import Blueprint, request, jsonify
from app.service.interview_service import InterviewService

interview_controller = Blueprint('interview_controller', __name__)
interview_service = InterviewService()

@interview_controller.route('/postInterview', methods=['POST'])
def create_interview():
    """ Post details for interviews """
    data = request.get_json()

    # Validate input data
    required_fields = ['type', 'job_id', 'interviewer_id', 'application_id', 'owner_id', 'schedule_date', 'status']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields.'}), 400

    try:
        # Create interview
        interview_id = interview_service.create_interview(data)
        return jsonify({'message': 'Interview created successfully!', 'interview_id': interview_id}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@interview_controller.route('/updateInterview/<int:interview_id>', methods=['PATCH'])
def update_interview(interview_id):
    """ Update interview details based on interview ID """
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided for update.'}), 400

    try:
        # Attempt to update the interview with provided fields
        success = interview_service.update_interview(interview_id, data)

        if success:
            return jsonify({'message': 'Interview updated successfully!'}), 200
        else:
            return jsonify({'message': 'Interview not found.'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@interview_controller.route('/getInterviewsByInterviewerId/<string:interviewer_id>', methods=['GET'])
def get_interviews_by_interviewer(interviewer_id):
    """ Get interviews by interviewer ID """
    try:
        interviews = interview_service.get_interviews_by_interviewer(interviewer_id)
        if interviews:
            return jsonify(interviews), 200
        else:
            return jsonify({'message': 'No interviews found for this interviewer.'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@interview_controller.route('/getInterviewsByOwnerId/<string:owner_id>', methods=['GET'])
def get_interviews_by_owner(owner_id):
    """ Get interviews by owner ID """
    try:
        interviews = interview_service.get_interviews_by_owner(owner_id)
        if interviews:
            return jsonify(interviews), 200
        else:
            return jsonify({'message': 'No interviews found for this owner.'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@interview_controller.route('/getInterviewsByApplicationId/<int:application_id>', methods=['GET'])
def get_interviews_by_application(application_id):
    """ Get interviews by application ID """
    try:
        interviews = interview_service.get_interviews_by_application(application_id)
        if interviews:
            return jsonify(interviews), 200
        else:
            return jsonify({'message': 'No interviews found for this application.'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@interview_controller.route('/getInterviewsByJobIdAndOwnerId/<int:job_id>/<string:owner_id>', methods=['GET'])
def get_interviews_by_job_and_owner(job_id, owner_id):
    """ Get interviews by job ID and owner ID """
    try:
        interviews = interview_service.get_interviews_by_job_and_owner(job_id, owner_id)
        if interviews:
            return jsonify(interviews), 200
        else:
            return jsonify({'message': 'No interviews found for this job and owner.'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@interview_controller.route('/getInterviewByJobIdAndInterviewerId/<int:job_id>/<string:interviewer_id>', methods=['GET'])
def get_interviews_by_job_and_interview(job_id, interviewer_id):
    """ Get interviews by job ID and interview ID """
    try:
        interview = interview_service.get_interviews_by_job_and_interview(job_id, interviewer_id)
        if interview:
            return jsonify(interview), 200
        else:
            return jsonify({'message': 'Interview not found for this job and interview ID.'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500