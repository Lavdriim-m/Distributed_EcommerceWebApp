from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.order import Order
from models.product import Product
from models.inventory_log import InventoryLog
from utils.decorators import role_required
from bson import json_util, ObjectId
import json

def create_orders_blueprint():
    orders_bp = Blueprint('orders', __name__)
    
    @orders_bp.route('/', methods=['POST'])
    @jwt_required()
    @role_required(['buyer'])
    def create_order():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data.get('products') or not isinstance(data['products'], list):
                return jsonify({'error': 'Products list is required'}), 400
            
            # Validate and process products
            product_list = []
            total_amount = 0
            sellers_to_notify = set()
            
            for item in data['products']:
                if not all(key in item for key in ['product_id', 'quantity']):
                    return jsonify({'error': 'Each product must have product_id and quantity'}), 400
                
                product = Product.find_by_id(item['product_id'])
                if not product:
                    return jsonify({'error': f'Product {item["product_id"]} not found'}), 404
                
                if product['stock'] < item['quantity']:
                    return jsonify({
                        'error': f'Insufficient stock for {product["name"]}. Available: {product["stock"]}',
                        'product_id': item['product_id'],
                        'available_stock': product['stock']
                    }), 409
                
                # Calculate item total
                item_total = product['price'] * item['quantity']
                total_amount += item_total
                
                product_list.append({
                    'product_id': ObjectId(item['product_id']),
                    'quantity': item['quantity'],
                    'price': product['price']
                })
                
                sellers_to_notify.add(str(product['seller_id']))
            
            # Create order
            order = Order(
                buyer_id=user_id,
                product_list=product_list,
                total_amount=total_amount
            )
            
            order_id = order.save()
            
            # Update product stocks and create inventory logs
            for item in data['products']:
                product = Product.find_by_id(item['product_id'])
                old_stock = product['stock']
                new_stock = old_stock - item['quantity']
                
                # Update stock
                Product.update_stock(item['product_id'], new_stock)
                
                # Log inventory change
                inventory_log = InventoryLog(
                    product_id=item['product_id'],
                    change_type='purchase',
                    old_stock=old_stock,
                    new_stock=new_stock,
                    reason=f'Order {order_id}'
                )
                inventory_log.save()
                
                # Emit real-time stock update
                if hasattr(current_app, 'emit_stock_update'):
                    current_app.emit_stock_update(item['product_id'], new_stock, product['name'])
                
                # Check for low stock alert
                if new_stock <= 5:
                    if hasattr(current_app, 'emit_low_stock_alert'):
                        current_app.emit_low_stock_alert(
                            str(product['seller_id']), 
                            item['product_id'], 
                            product['name'], 
                            new_stock
                        )
            
            # Notify sellers about new orders
            order_data = {
                'order_id': str(order_id),
                'timestamp': order.timestamp.isoformat(),
                'total_amount': total_amount,
                'product_count': len(product_list)
            }
            
            for seller_id in sellers_to_notify:
                if hasattr(current_app, 'emit_order_notification'):
                    current_app.emit_order_notification(seller_id, order_data)
            
            return jsonify({
                'message': 'Order placed successfully',
                'order_id': str(order_id),
                'total_amount': total_amount
            }), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @orders_bp.route('/my-orders', methods=['GET'])
    @jwt_required()
    @role_required(['buyer'])
    def get_my_orders():
        try:
            user_id = get_jwt_identity()
            orders = Order.find_by_buyer(user_id)
            
            orders_json = json.loads(json_util.dumps(orders))
            return jsonify({'orders': orders_json}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @orders_bp.route('/seller-orders', methods=['GET'])
    @jwt_required()
    @role_required(['seller'])
    def get_seller_orders():
        try:
            user_id = get_jwt_identity()
            orders = Order.find_by_seller(user_id)
            
            orders_json = json.loads(json_util.dumps(orders))
            return jsonify({'orders': orders_json}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @orders_bp.route('/<order_id>/status', methods=['PUT'])
    @jwt_required()
    @role_required(['seller', 'admin'])
    def update_order_status(order_id):
        try:
            data = request.get_json()
            
            if not data.get('status') or data['status'] not in ['placed', 'completed', 'cancelled']:
                return jsonify({'error': 'Invalid status'}), 400
            
            # Find order
            order = Order.find_by_id(order_id)
            if not order:
                return jsonify({'error': 'Order not found'}), 404
            
            # Update status
            Order.update_order_status(order_id, data['status'])
            
            return jsonify({'message': 'Order status updated successfully'}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @orders_bp.route('/statistics', methods=['GET'])
    @jwt_required()
    @role_required(['admin'])
    def get_order_statistics():
        try:
            stats = Order.get_order_statistics()
            stats_json = json.loads(json_util.dumps(stats))
            
            return jsonify({'statistics': stats_json}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return orders_bp