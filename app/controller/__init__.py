from flask import Blueprint
from .linkedin_controller import linkedin_bp
from .user_controller import user_controller  
from .job_controller import job_controller
from .candidate_controller import candidate_controller
from .application_controller import application_controller
from .interview_controller import interview_controller
from .openai_controller import openai_controller
from .ats_controller import ats_controller

controllers_bp = Blueprint('controllers', __name__)

controllers_bp.register_blueprint(linkedin_bp)
controllers_bp.register_blueprint(user_controller)  
controllers_bp.register_blueprint(job_controller)
controllers_bp.register_blueprint(candidate_controller)
controllers_bp.register_blueprint(application_controller)
controllers_bp.register_blueprint(interview_controller)
controllers_bp.register_blueprint(openai_controller)
controllers_bp.register_blueprint(ats_controller)