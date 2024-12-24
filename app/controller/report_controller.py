
from flask import Blueprint, request, jsonify
from app.service.report_service import ReportService

report_controller = Blueprint('report_controller', __name__)
report_service = ReportService()

@report_controller.route('/createReport', methods=['POST'])
def create_report():
    """ Insert a new report into the Report table """
    data = request.get_json()

    # Validate required fields
    if not data or 'reportName' not in data or 'createdBy' not in data:
        return jsonify({'message': 'Missing required fields: reportName, createdBy'}), 400

    try:
        report_id = report_service.create_report(data)
        return jsonify({'message': 'Report created successfully!', 'report_id': report_id}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@report_controller.route('/getAllReports', methods=['GET'])
def get_reports():
    """ Fetch all reports from the Report table """
    try:
        reports = report_service.get_all_reports()
        return jsonify(reports), 200  # Return reports as JSON
    except Exception as e:
        return jsonify({'message': str(e)}), 500