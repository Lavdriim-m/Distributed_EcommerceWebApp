from datetime import datetime, timedelta
from bson import ObjectId
from database.connection import db

class Order:
    def __init__(self, buyer_id, product_list, total_amount):
        self.buyer_id = ObjectId(buyer_id)
        self.product_list = product_list
        self.total_amount = float(total_amount)
        self.status = 'placed'
        self.timestamp = datetime.utcnow()
    
    def save(self):
        """Save order to database"""
        order_data = {
            'buyer_id': self.buyer_id,
            'product_list': self.product_list,
            'total_amount': self.total_amount,
            'status': self.status,
            'timestamp': self.timestamp
        }
        result = db.orders.insert_one(order_data)
        return result.inserted_id
    
    @staticmethod
    def find_by_id(order_id):
        """Find order by ID"""
        return db.orders.find_one({'_id': ObjectId(order_id)})
    
    @staticmethod
    def find_by_buyer(buyer_id):
        """Find all orders by buyer"""
        return list(db.orders.find({'buyer_id': ObjectId(buyer_id)}))
    
    @staticmethod
    def find_by_seller(seller_id):
        """Find orders containing products from specific seller"""
        pipeline = [
            {'$lookup': {
                'from': 'products',
                'localField': 'product_list.product_id',
                'foreignField': '_id',
                'as': 'product_details'
            }},
            {'$match': {
                'product_details.seller_id': ObjectId(seller_id)
            }}
        ]
        return list(db.orders.aggregate(pipeline))
    
    @staticmethod
    def get_recent_orders(days=30):
        """Get orders from last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return list(db.orders.find({'timestamp': {'$gte': cutoff_date}}))
    
    @staticmethod
    def update_order_status(order_id, status):
        """Update order status"""
        return db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': {'status': status}}
        )
    
    @staticmethod
    def get_order_statistics():
        """Get order statistics for admin dashboard"""
        pipeline = [
            {'$group': {
                '_id': '$status',
                'count': {'$sum': 1},
                'total_amount': {'$sum': '$total_amount'}
            }}
        ]
        return list(db.orders.aggregate(pipeline))
    
    @staticmethod
    def get_buyer_order_history(buyer_id, limit=10):
        """Get buyer's recent order history"""
        return list(db.orders.find(
            {'buyer_id': ObjectId(buyer_id)},
            sort=[('timestamp', -1)],
            limit=limit
        ))