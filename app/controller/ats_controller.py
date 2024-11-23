from flask import Blueprint, jsonify

from app.service.ats_service import ATSService

ats_controller = Blueprint('ats_controller', __name__)
application_service = ATSService()

@ats_controller.route('/rankCandidatesUsingOpenai/<int:job_id>', methods=['GET'])
def track_applications_using_openai(job_id):
    """ Endpoint to track applications by job ID and rank candidates. """
    try:
        results = application_service.fetch_and_rank_applications(job_id)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ats_controller.route('/rankCandidatesUsingNLP/<int:job_id>', methods=['GET'])
def track_applications_using_NLP(job_id):
    """ Endpoint to track applications by job ID and rank candidates. """
    try:
        results = application_service.fetch_and_rank_applicationsNLP(job_id)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

