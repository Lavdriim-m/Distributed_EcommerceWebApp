from bson import ObjectId
from datetime import datetime
from database.connection import db

class Product:
    def __init__(self, seller_id, name, description, price, stock, category):
        self.seller_id = ObjectId(seller_id)
        self.name = name
        self.description = description
        self.price = float(price)
        self.stock = int(stock)
        self.category = category
        self.created_at = datetime.utcnow()
    
    def save(self):
        """Save product to database"""
        product_data = {
            'seller_id': self.seller_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'category': self.category,
            'created_at': self.created_at
        }
        result = db.products.insert_one(product_data)
        return result.inserted_id
    
    @staticmethod
    def find_by_id(product_id):
        """Find product by ID"""
        return db.products.find_one({'_id': ObjectId(product_id)})
    
    @staticmethod
    def find_by_seller(seller_id):
        """Find all products by seller"""
        return list(db.products.find({'seller_id': ObjectId(seller_id)}))
    
    @staticmethod
    def get_all_products(filters=None):
        """Get all products with optional filters"""
        query = {}
        
        if filters:
            if 'category' in filters and filters['category']:
                query['category'] = filters['category']
            
            if 'search' in filters and filters['search']:
                query['$text'] = {'$search': filters['search']}
            
            if 'min_price' in filters and filters['min_price'] not in (None, ''):
                query['price'] = query.get('price', {})
                query['price']['$gte'] = float(filters['min_price'])

            if 'max_price' in filters and filters['max_price'] not in (None, ''):
                query['price'] = query.get('price', {})
                query['price']['$lte'] = float(filters['max_price'])
            
            if 'in_stock' in filters and filters['in_stock']:
                query['stock'] = {'$gt': 0}
        
        return list(db.products.find(query))
    
    @staticmethod
    def update_product(product_id, update_data):
        """Update product information"""
        return db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': update_data}
        )
    
    @staticmethod
    def update_stock(product_id, new_stock):
        """Update product stock"""
        return db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': {'stock': new_stock}}
        )
    
    @staticmethod
    def delete_product(product_id):
        """Delete product"""
        return db.products.delete_one({'_id': ObjectId(product_id)})
    
    @staticmethod
    def get_low_stock_products(threshold=5):
        """Get products with low stock"""
        return list(db.products.find({'stock': {'$lte': threshold}}))
    
    @staticmethod
    def get_categories():
        """Get all unique categories"""
        return db.products.distinct('category')
    
    @staticmethod
    def get_top_selling_products(limit=5):
        """Get top selling products based on order history"""
        pipeline = [
            {'$lookup': {
                'from': 'orders',
                'localField': '_id',
                'foreignField': 'product_list.product_id',
                'as': 'orders'
            }},
            {'$addFields': {
                'total_sold': {'$sum': '$orders.product_list.quantity'}
            }},
            {'$sort': {'total_sold': -1}},
            {'$limit': limit}
        ]
        return list(db.products.aggregate(pipeline))