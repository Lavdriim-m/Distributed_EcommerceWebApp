from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User
import bcrypt

def create_auth_blueprint():
    auth_bp = Blueprint('auth', __name__)
    
    @auth_bp.route('/register', methods=['POST'])
    def register():
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'email', 'password', 'role']
            if not all(field in data for field in required_fields):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Check if user already exists
            if User.find_by_email(data['email']):
                return jsonify({'error': 'User with this email already exists'}), 409
            
            # Validate role
            if data['role'] not in ['buyer', 'seller', 'admin']:
                return jsonify({'error': 'Invalid role'}), 400
            
            # Create new user
            user = User(
                name=data['name'],
                email=data['email'],
                password=data['password'],
                role=data['role']
            )
            
            user_id = user.save()
            
            # Create access token
            access_token = create_access_token(
                identity=str(user_id),
                additional_claims={'role': data['role']}
            )
            
            return jsonify({
                'message': 'User registered successfully',
                'access_token': access_token,
                'user': {
                    'id': str(user_id),
                    'name': data['name'],
                    'email': data['email'],
                    'role': data['role']
                }
            }), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @auth_bp.route('/login', methods=['POST'])
    def login():
        try:
            data = request.get_json()
            
            if not data.get('email') or not data.get('password'):
                return jsonify({'error': 'Email and password are required'}), 400
            
            # Find user by email
            user = User.find_by_email(data['email'])
            if not user:
                return jsonify({'error': 'Invalid credentials'}), 401
            
            # Check password
            if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password_hash']):
                return jsonify({'error': 'Invalid credentials'}), 401
            
            # Create access token
            access_token = create_access_token(
                identity=str(user['_id']),
                additional_claims={'role': user['role']}
            )
            
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user': {
                    'id': str(user['_id']),
                    'name': user['name'],
                    'email': user['email'],
                    'role': user['role']
                }
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @auth_bp.route('/profile', methods=['GET'])
    @jwt_required()
    def get_profile():
        try:
            user_id = get_jwt_identity()
            user = User.find_by_id(user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            return jsonify({
                'user': {
                    'id': str(user['_id']),
                    'name': user['name'],
                    'email': user['email'],
                    'role': user['role'],
                    'created_at': user['created_at'].isoformat()
                }
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return auth_bp