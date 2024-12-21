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
    
@category_controller.route('/updateCategoryById/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """ Update category details based on ID """
    data = request.get_json()

    # Validate input data
    if not data:
        return jsonify({'message': 'No data provided for update.'}), 400

    try:
        # Update category
        rows_affected = category_service.update_category(category_id, data)
        if rows_affected == 0:
            return jsonify({'message': 'Category not found or no changes made.'}), 404
        return jsonify({'message': 'Category updated successfully!'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@category_controller.route('/deleteCategoryById/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """ Delete a category based on its ID """
    try:
        rows_affected = category_service.delete_category(category_id)
        if rows_affected == 0:
            return jsonify({'message': 'Category not found.'}), 404
        return jsonify({'message': 'Category deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500