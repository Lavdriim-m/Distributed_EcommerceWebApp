from datetime import datetime, timedelta
from bson import ObjectId
from database.connection import db

class InventoryLog:
    def __init__(self, product_id, change_type, old_stock, new_stock, reason=""):
        self.product_id = ObjectId(product_id)
        self.change_type = change_type  # 'restock', 'purchase', 'adjustment'
        self.old_stock = int(old_stock)
        self.new_stock = int(new_stock)
        self.reason = reason
        self.timestamp = datetime.utcnow()
    
    def save(self):
        """Save inventory log to database"""
        log_data = {
            'product_id': self.product_id,
            'change_type': self.change_type,
            'old_stock': self.old_stock,
            'new_stock': self.new_stock,
            'reason': self.reason,
            'timestamp': self.timestamp
        }
        result = db.inventory_logs.insert_one(log_data)
        return result.inserted_id
    
    @staticmethod
    def find_by_product(product_id, limit=50):
        """Find inventory logs for a specific product"""
        return list(db.inventory_logs.find(
            {'product_id': ObjectId(product_id)},
            sort=[('timestamp', -1)],
            limit=limit
        ))
    
    @staticmethod
    def get_recent_logs(days=7):
        """Get recent inventory logs"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return list(db.inventory_logs.find(
            {'timestamp': {'$gte': cutoff_date}},
            sort=[('timestamp', -1)]
        ))
    
    @staticmethod
    def get_stock_changes_summary():
        """Get summary of stock changes by type"""
        pipeline = [
            {'$group': {
                '_id': '$change_type',
                'count': {'$sum': 1},
                'total_change': {
                    '$sum': {'$subtract': ['$new_stock', '$old_stock']}
                }
            }}
        ]
        return list(db.inventory_logs.aggregate(pipeline))