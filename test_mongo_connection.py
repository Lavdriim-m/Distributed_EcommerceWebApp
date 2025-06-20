from pymongo import MongoClient
import os

# Test your connection string here
MONGO_URI = "mongodb+srv://your-username:your-password@your-cluster.mongodb.net/distributed_ecommerce?retryWrites=true&w=majority"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB Atlas!")
    
    # Test database access
    db = client['distributed_ecommerce']
    collections = db.list_collection_names()
    print(f"✅ Database 'distributed_ecommerce' accessible. Collections: {collections}")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
finally:
    if 'client' in locals():
        client.close() 