// MongoDB Replica Set Initialization Script
// Run this script after starting MongoDB containers

rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongo1:27017" },
    { _id: 1, host: "mongo2:27018" },
    { _id: 2, host: "mongo3:27019" }
  ]
});

// Wait for replica set to be ready
sleep(5000);

// Create demo users
use('distributed_ecommerce');

// Demo buyer
db.users.insertOne({
  name: "Demo Buyer",
  email: "buyer@demo.com",
  password_hash: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3QJflLxQjm", // demo123
  role: "buyer",
  created_at: new Date()
});

// Demo seller
db.users.insertOne({
  name: "Demo Seller",
  email: "seller@demo.com",
  password_hash: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3QJflLxQjm", // demo123
  role: "seller",
  created_at: new Date()
});

// Demo admin
db.users.insertOne({
  name: "Demo Admin",
  email: "admin@demo.com",
  password_hash: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3QJflLxQjm", // demo123
  role: "admin",
  created_at: new Date()
});

// Get seller ID for demo products
const seller = db.users.findOne({email: "seller@demo.com"});

// Demo products
const demoProducts = [
  {
    seller_id: seller._id,
    name: "Wireless Bluetooth Headphones",
    description: "High-quality wireless headphones with noise cancellation and 30-hour battery life.",
    price: 99.99,
    stock: 25,
    category: "Electronics",
    created_at: new Date()
  },
  {
    seller_id: seller._id,
    name: "Smart Fitness Watch",
    description: "Advanced fitness tracker with heart rate monitoring, GPS, and smartphone integration.",
    price: 199.99,
    stock: 15,
    category: "Electronics",
    created_at: new Date()
  },
  {
    seller_id: seller._id,
    name: "Organic Coffee Beans",
    description: "Premium organic coffee beans sourced from sustainable farms. Medium roast.",
    price: 24.99,
    stock: 50,
    category: "Food & Beverages",
    created_at: new Date()
  },
  {
    seller_id: seller._id,
    name: "Yoga Mat",
    description: "Non-slip yoga mat made from eco-friendly materials. Perfect for home workouts.",
    price: 39.99,
    stock: 8,
    category: "Sports & Fitness",
    created_at: new Date()
  },
  {
    seller_id: seller._id,
    name: "LED Desk Lamp",
    description: "Adjustable LED desk lamp with multiple brightness levels and USB charging port.",
    price: 49.99,
    stock: 3,
    category: "Home & Office",
    created_at: new Date()
  }
];

db.products.insertMany(demoProducts);

print("Demo data inserted successfully!");