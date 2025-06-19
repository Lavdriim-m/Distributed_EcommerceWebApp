from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import os
from datetime import datetime, timedelta
import bcrypt
import json
from bson import ObjectId, json_util
from dotenv import load_dotenv

from database.connection import db
from models.user import User
from models.product import Product
from models.order import Order
from models.inventory_log import InventoryLog
from routes.auth import create_auth_blueprint
from routes.products import create_products_blueprint
from routes.orders import create_orders_blueprint
from routes.admin import create_admin_blueprint
from utils.decorators import role_required

load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
jwt = JWTManager(app)
CORS(app,
    origins=["http://localhost:5173"],
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE"]
    )
socketio = SocketIO(
    app,
    cors_allowed_origins=["http://localhost:5173"],
    async_mode='eventlet',
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=1e8,
    logger=True,
    engineio_logger=True
)

# Register blueprints
app.register_blueprint(create_auth_blueprint(), url_prefix='/api/auth')
app.register_blueprint(create_products_blueprint(), url_prefix='/api/products')
app.register_blueprint(create_orders_blueprint(), url_prefix='/api/orders')
app.register_blueprint(create_admin_blueprint(), url_prefix='/api/admin')

# Store connected users for real-time updates
connected_users = {}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for distributed systems monitoring"""
    try:
        # Test database connection
        db.admin.command('ping')
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'node_id': os.getenv('NODE_ID', 'node-1')
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@socketio.on_error()
def error_handler(e):
    print(f'Socket.IO error: {e}')
    return {'error': str(e)}

@socketio.on('connect')
def handle_connect():
    try:
        print(f'Client connected: {request.sid}')
        emit('connection_response', {'status': 'Connected to server'})
    except Exception as e:
        print(f'Connection error: {e}')
        return False

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')
    # Remove user from connected users
    if request.sid in connected_users:
        del connected_users[request.sid]

@socketio.on('join_user_room')
def handle_join_user_room(data):
    """Join user to their personal room for targeted notifications"""
    user_id = data.get('user_id')
    if user_id:
        join_room(f"user_{user_id}")
        connected_users[request.sid] = user_id
        print(f'User {user_id} joined their room')

@socketio.on('join_sellers_room')
def handle_join_sellers_room():
    """Join sellers to a common room for inventory updates"""
    join_room('sellers')
    print('User joined sellers room')

def emit_stock_update(product_id, new_stock, product_name):
    """Emit stock update to all connected clients"""
    socketio.emit('stock_update', {
        'product_id': str(product_id),
        'new_stock': new_stock,
        'product_name': product_name,
        'timestamp': datetime.utcnow().isoformat()
    })

def emit_low_stock_alert(seller_id, product_id, product_name, current_stock):
    """Emit low stock alert to specific seller"""
    socketio.emit('low_stock_alert', {
        'product_id': str(product_id),
        'product_name': product_name,
        'current_stock': current_stock,
        'timestamp': datetime.utcnow().isoformat()
    }, room=f"user_{seller_id}")

def emit_order_notification(seller_id, order_data):
    """Emit new order notification to seller"""
    socketio.emit('new_order', order_data, room=f"user_{seller_id}")

# Make these functions available to other modules
app.emit_stock_update = emit_stock_update
app.emit_low_stock_alert = emit_low_stock_alert
app.emit_order_notification = emit_order_notification

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    node_id = os.getenv('NODE_ID', 'node-1')
    
    print(f"Starting {node_id} on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=True)