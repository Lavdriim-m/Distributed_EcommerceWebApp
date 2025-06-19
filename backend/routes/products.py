from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.product import Product
from models.inventory_log import InventoryLog
from utils.decorators import role_required
from bson import json_util
import json
from functools import wraps
import asyncio

def create_products_blueprint():
    products_bp = Blueprint('products', __name__)
    
    def async_route(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(f(*args, **kwargs))
            finally:
                loop.close()
        return wrapped
    
    @products_bp.route('/', methods=['GET'])
    def get_products():
        try:
            # Get query parameters for filtering
            filters = {
                'category': request.args.get('category'),
                'search': request.args.get('search'),
                'min_price': request.args.get('min_price'),
                'max_price': request.args.get('max_price'),
                'in_stock': request.args.get('in_stock') == 'true'
            }
            
            products = Product.get_all_products(filters)
            products_json = json.loads(json_util.dumps(products))
            
            return jsonify({'products': products_json}), 200
            
        except Exception as e:
            current_app.logger.error(f"Error in get_products: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @products_bp.route('/<product_id>', methods=['GET'])
    def get_product(product_id):
        try:
            product = Product.find_by_id(product_id)
            if not product:
                return jsonify({'error': 'Product not found'}), 404
            
            product_json = json.loads(json_util.dumps(product))
            return jsonify({'product': product_json}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @products_bp.route('/', methods=['POST'])
    @jwt_required()
    @role_required(['seller', 'admin'])
    def create_product():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'description', 'price', 'stock', 'category']
            if not all(field in data for field in required_fields):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Create new product
            product = Product(
                seller_id=user_id,
                name=data['name'],
                description=data['description'],
                price=data['price'],
                stock=data['stock'],
                category=data['category']
            )
            
            product_id = product.save()
            
            # Log initial inventory
            inventory_log = InventoryLog(
                product_id=product_id,
                change_type='restock',
                old_stock=0,
                new_stock=data['stock'],
                reason='Initial stock'
            )
            inventory_log.save()
            
            return jsonify({
                'message': 'Product created successfully',
                'product_id': str(product_id)
            }), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @products_bp.route('/<product_id>', methods=['PUT'])
    @jwt_required()
    @role_required(['seller', 'admin'])
    def update_product(product_id):
        try:
            user_id = get_jwt_identity()
            user_role = get_jwt().get('role')
            data = request.get_json()
            
            # Find product
            product = Product.find_by_id(product_id)
            if not product:
                return jsonify({'error': 'Product not found'}), 404
            
            # Check if user owns the product (unless admin)
            if user_role != 'admin' and str(product['seller_id']) != user_id:
                return jsonify({'error': 'Unauthorized'}), 403
            
            # Track stock changes
            old_stock = product['stock']
            new_stock = data.get('stock', old_stock)
            
            # Update product
            update_data = {}
            for field in ['name', 'description', 'price', 'stock', 'category']:
                if field in data:
                    update_data[field] = data[field]
            
            Product.update_product(product_id, update_data)
            
            # Log stock change if stock was updated
            if old_stock != new_stock:
                inventory_log = InventoryLog(
                    product_id=product_id,
                    change_type='restock' if new_stock > old_stock else 'adjustment',
                    old_stock=old_stock,
                    new_stock=new_stock,
                    reason='Manual update'
                )
                inventory_log.save()
                
                # Emit real-time stock update
                if hasattr(current_app, 'emit_stock_update'):
                    current_app.emit_stock_update(product_id, new_stock, product['name'])
                
                # Check for low stock
                if new_stock <= 5:
                    if hasattr(current_app, 'emit_low_stock_alert'):
                        current_app.emit_low_stock_alert(
                            str(product['seller_id']), 
                            product_id, 
                            product['name'], 
                            new_stock
                        )
            
            return jsonify({'message': 'Product updated successfully'}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @products_bp.route('/<product_id>', methods=['DELETE'])
    @jwt_required()
    @role_required(['seller', 'admin'])
    def delete_product(product_id):
        try:
            user_id = get_jwt_identity()
            user_role = get_jwt().get('role')
            
            # Find product
            product = Product.find_by_id(product_id)
            if not product:
                return jsonify({'error': 'Product not found'}), 404
            
            # Check if user owns the product (unless admin)
            if user_role != 'admin' and str(product['seller_id']) != user_id:
                return jsonify({'error': 'Unauthorized'}), 403
            
            # Delete product
            Product.delete_product(product_id)
            
            return jsonify({'message': 'Product deleted successfully'}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @products_bp.route('/my-products', methods=['GET'])
    @jwt_required()
    @role_required(['seller'])
    def get_my_products():
        try:
            user_id = get_jwt_identity()
            products = Product.find_by_seller(user_id)
            
            products_json = json.loads(json_util.dumps(products))
            return jsonify({'products': products_json}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @products_bp.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Product.get_categories()
            return jsonify({'categories': categories}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @products_bp.route('/top-selling', methods=['GET'])
    @jwt_required()
    @role_required(['seller', 'admin'])
    def get_top_selling():
        try:
            limit = int(request.args.get('limit', 5))
            products = Product.get_top_selling_products(limit)
            
            products_json = json.loads(json_util.dumps(products))
            return jsonify({'products': products_json}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return products_bp