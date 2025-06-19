from bson import ObjectId
from datetime import datetime
import bcrypt
from database.connection import db

class User:
    def __init__(self, name, email, password, role='buyer'):
        self.name = name
        self.email = email
        self.password_hash = self._hash_password(password)
        self.role = role
        self.created_at = datetime.utcnow()
    
    def _hash_password(self, password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)
    
    def save(self):
        """Save user to database"""
        user_data = {
            'name': self.name,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'created_at': self.created_at
        }
        result = db.users.insert_one(user_data)
        return result.inserted_id
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        return db.users.find_one({'email': email})
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        return db.users.find_one({'_id': ObjectId(user_id)})
    
    @staticmethod
    def get_all_users():
        """Get all users (admin only)"""
        return list(db.users.find({}, {'password_hash': 0}))
    
    @staticmethod
    def update_user(user_id, update_data):
        """Update user information"""
        return db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
    
    @staticmethod
    def delete_user(user_id):
        """Delete user"""
        return db.users.delete_one({'_id': ObjectId(user_id)})
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at
        }