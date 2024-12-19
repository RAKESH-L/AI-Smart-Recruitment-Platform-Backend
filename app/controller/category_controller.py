import os
from flask import Blueprint, request, jsonify
from app.service.category_service import CategoryService

category_controller = Blueprint('category_controller', __name__)
category_service = CategoryService()

@category_controller.route('/createCategories', methods=['POST'])
def create_category():
    """ Post details for categories """
    data = request.get_json()

    # Validate input data
    required_fields = ['category_type', 'category_name']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields.'}), 400

    try:
        # Create category
        category_id = category_service.create_category(data)
        return jsonify({'message': 'Category created successfully!', 'category_id': category_id}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@category_controller.route('/fetchAllCategories', methods=['GET'])
def get_categories():
    """ Get all categories """
    try:
        categories = category_service.get_all_categories()
        return jsonify(categories), 200  # Return categories as JSON
    except Exception as e:
        return jsonify({'message': str(e)}), 500