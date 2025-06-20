import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import time

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'distributed_ecommerce')

def connect_to_mongo(max_retries=5, retry_delay=5):
    retries = 0
    while retries < max_retries:
        try:
            # Check if we're using MongoDB Atlas (cloud) or local replica set
            if 'mongodb+srv://' in MONGO_URI or 'mongodb.net' in MONGO_URI:
                # MongoDB Atlas connection (cloud)
                client = MongoClient(
                    MONGO_URI,
                    serverSelectionTimeoutMS=10000,
                    maxPoolSize=50,
                    minPoolSize=10,
                    maxIdleTimeMS=30000,
                    waitQueueTimeoutMS=10000
                )
            else:
                # Local replica set connection
                client = MongoClient(
                    MONGO_URI,
                    serverSelectionTimeoutMS=10000,
                    replicaSet='rs0',
                    readPreference='secondaryPreferred',
                    maxPoolSize=50,
                    minPoolSize=10,
                    maxIdleTimeMS=30000,
                    waitQueueTimeoutMS=10000
                )
            
            client.admin.command('ping')
            print("Successfully connected to MongoDB")
            return client
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            retries += 1
            print(f"Connection attempt {retries} failed: {e}")
            if retries < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    raise ConnectionFailure("Failed to connect to MongoDB after multiple attempts")

try:
    client = connect_to_mongo()
    db = client[DATABASE_NAME]
    
    # Create indexes
    db.users.create_index("email", unique=True)
    db.products.create_index([("name", "text"), ("description", "text")])
    db.products.create_index("seller_id")
    db.products.create_index("category")
    db.orders.create_index("buyer_id")
    db.orders.create_index("timestamp")
    db.inventory_logs.create_index("product_id")
    db.inventory_logs.create_index("timestamp")
    
    print("Database indexes created successfully")
    
except Exception as e:
    print(f"Database setup error: {e}")
    raise e