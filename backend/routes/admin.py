from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.product import Product
from models.order import Order
from models.inventory_log import InventoryLog
from utils.decorators import role_required
from bson import json_util
import json

def create_admin_blueprint():
    admin_bp = Blueprint('admin', __name__)
    
    @admin_bp.route('/users', methods=['GET'])
    @jwt_required()
    @role_required(['admin'])
    def get_all_users():
        try:
            users = User.get_all_users()
            users_json = json.loads(json_util.dumps(users))
            
            return jsonify({'users': users_json}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @admin_bp.route('/products', methods=['GET'])
    @jwt_required()
    @role_required(['admin'])
    def get_all_products():
        try:
            products = Product.get_all_products()
            products_json = json.loads(json_util.dumps(products))
            
            return jsonify({'products': products_json}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @admin_bp.route('/orders', methods=['GET'])
    @jwt_required()
    @role_required(['admin'])
    def get_all_orders():
        try:
            # Get recent orders (last 30 days by default)
            days = int(request.args.get('days', 30))
            orders = Order.get_recent_orders(days)
            orders_json = json.loads(json_util.dumps(orders))
            
            return jsonify({'orders': orders_json}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @admin_bp.route('/dashboard', methods=['GET'])
    @jwt_required()
    @role_required(['admin'])
    def get_dashboard_stats():
        try:
            # Get various statistics for admin dashboard
            stats = {}
            
            # User statistics
            all_users = User.get_all_users()
            stats['total_users'] = len(all_users)
            stats['users_by_role'] = {}
            for user in all_users:
                role = user['role']
                stats['users_by_role'][role] = stats['users_by_role'].get(role, 0) + 1
            
            # Product statistics
            all_products = Product.get_all_products()
            stats['total_products'] = len(all_products)
            stats['low_stock_products'] = len(Product.get_low_stock_products())
            
            # Order statistics
            order_stats = Order.get_order_statistics()
            stats['order_statistics'] = json.loads(json_util.dumps(order_stats))
            
            # Inventory logs summary
            inventory_stats = InventoryLog.get_stock_changes_summary()
            stats['inventory_statistics'] = json.loads(json_util.dumps(inventory_stats))
            
            return jsonify({'dashboard': stats}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @admin_bp.route('/users/<user_id>', methods=['DELETE'])
    @jwt_required()
    @role_required(['admin'])
    def delete_user(user_id):
        try:
            # Find user
            user = User.find_by_id(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Delete user
            User.delete_user(user_id)
            
            return jsonify({'message': 'User deleted successfully'}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @admin_bp.route('/products/<product_id>/disable', methods=['PUT'])
    @jwt_required()
    @role_required(['admin'])
    def disable_product(product_id):
        try:
            # Find product
            product = Product.find_by_id(product_id)
            if not product:
                return jsonify({'error': 'Product not found'}), 404
            
            # Set stock to 0 to effectively disable
            Product.update_stock(product_id, 0)
            
            # Log the action
            inventory_log = InventoryLog(
                product_id=product_id,
                change_type='adjustment',
                old_stock=product['stock'],
                new_stock=0,
                reason='Disabled by admin'
            )
            inventory_log.save()
            
            return jsonify({'message': 'Product disabled successfully'}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @admin_bp.route('/system-health', methods=['GET'])
    @jwt_required()
    @role_required(['admin'])
    def get_system_health():
        try:
            # Basic system health metrics
            from database.connection import db
            
            # Test database connection
            db.admin.command('ping')
            
            # Get collection stats
            health_data = {
                'database_status': 'connected',
                'collections': {
                    'users': db.users.count_documents({}),
                    'products': db.products.count_documents({}),
                    'orders': db.orders.count_documents({}),
                    'inventory_logs': db.inventory_logs.count_documents({})
                },
                'timestamp': json.loads(json_util.dumps({'timestamp': datetime.utcnow()}))
            }
            
            return jsonify({'health': health_data}), 200
            
        except Exception as e:
            return jsonify({
                'health': {
                    'database_status': 'error',
                    'error': str(e)
                }
            }), 500
    
    return admin_bp