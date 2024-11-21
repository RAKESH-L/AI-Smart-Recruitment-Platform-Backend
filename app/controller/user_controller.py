from flask import Blueprint, request, jsonify
from app.service.user_service import UserService
import bcrypt

user_controller = Blueprint('user_controller', __name__)
user_service = UserService()

@user_controller.route('/postUser', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    required_fields = ['employee_id','full_name', 'username', 'password', 'phone_number', 'role', 'email']
    
    # Check for required fields
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing field: {field}'}), 400

    try:
        # Call the service to add the user
        user_id = user_service.create_user(data)
        return jsonify({'user_id': user_id, 'message': 'User created successfully!'}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@user_controller.route('/getUser/<int:employee_id>', methods=['GET'])
def get_user(employee_id):
    try:
        user = user_service.get_user_by_id(employee_id)
        if user:
            return jsonify(user), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@user_controller.route('/updateUser/<int:employee_id>', methods=['PUT'])
def update_user(employee_id):
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    # Ensure any required fields or validations based on your application logic
    try:
        updated_user = user_service.update_user(employee_id, data)
        
        if updated_user:
            return jsonify({'message': 'User updated successfully!'}), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@user_controller.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or ('employeeId' not in data and 'username' not in data and 'email' not in data) or 'password' not in data:
        return jsonify({'message': 'Missing required fields'}), 400

    employeeId = data.get('employeeId')
    username = data.get('username')  # Can be None
    email = data.get('email')  # Can be None
    password = data['password']

    try:
        user = user_service.get_user_by_credentials(username, email, employeeId)

        # Check if user exists and password matches
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'message': 'Access granted!', 'employee_id': user['employee_id'], 'role': user['role'],"authenticated": True}), 200
        else:
            return jsonify({'message': 'Invalid credentials', "authenticated": False}), 401
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    

@user_controller.route('/getAllUsers', methods=['GET'])
def get_users():
    """ Fetch all users """
    try:
        users = user_service.get_all_users()
        return jsonify(users), 200  # Return users as JSON
    except Exception as e:
        return jsonify({'message': str(e)}), 500