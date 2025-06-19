# Distributed E-Commerce Web Application

A comprehensive distributed e-commerce platform built with Python Flask backend and React frontend, designed for university courses in Distributed Systems and NoSQL Databases.

## 🏗️ Architecture

### Backend (Python Flask)
- **Flask** with Flask-SocketIO for real-time communication
- **MongoDB** with replica set configuration for high availability
- **JWT-based authentication** with role-based access control
- **RESTful API** design with proper error handling
- **Real-time inventory updates** using WebSocket connections

### Frontend (React + TypeScript)
- **React 18** with TypeScript for type safety
- **Tailwind CSS** for modern, responsive design
- **Socket.IO client** for real-time updates
- **Chart.js** for analytics and data visualization
- **Context API** for state management

### Database (MongoDB)
- **Replica Set** configuration for fault tolerance
- **Complex aggregation queries** for analytics
- **Proper indexing** for performance optimization
- **Document-based** schema design

## 🚀 Features

### For Buyers
- ✅ User registration and authentication
- ✅ Browse and search products with advanced filters
- ✅ Real-time stock updates and notifications
- ✅ Shopping cart with quantity management
- ✅ Order placement and history tracking
- ✅ Responsive design for all devices

### For Sellers
- ✅ Product management (CRUD operations)
- ✅ Real-time inventory tracking
- ✅ Low stock alerts and notifications
- ✅ Sales analytics and statistics
- ✅ Order notifications
- ✅ Dashboard with key metrics

### For Admins
- ✅ User management and oversight
- ✅ Product moderation capabilities
- ✅ System health monitoring
- ✅ Analytics dashboard with charts
- ✅ Order statistics and trends
- ✅ Database health checks

### Real-Time Features
- ✅ Live stock updates across all clients
- ✅ Instant notifications for low stock
- ✅ Real-time order notifications for sellers
- ✅ WebSocket-based communication

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 16+
- MongoDB 5.0+
- Docker (optional, for containerized deployment)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd distributed-ecommerce-app
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your configuration
   python app.py
   ```

3. **Frontend Setup**
   ```bash
   npm install
   npm run dev
   ```

4. **MongoDB Setup**
   ```bash
   # Start MongoDB locally
   mongod --replSet rs0
   
   # Initialize replica set (in mongo shell)
   rs.initiate()
   ```

### Docker Deployment

1. **Start the entire stack**
   ```bash
   cd backend
   docker-compose up -d
   ```

2. **Initialize MongoDB replica set**
   ```bash
   docker exec -it mongo1 mongo --eval "$(cat init-replica-set.js)"
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000
   - Load Balancer: http://localhost:80

## 📊 Database Schema

### Collections

#### Users Collection
```javascript
{
  "_id": ObjectId,
  "name": String,
  "email": String (unique),
  "password_hash": String,
  "role": String (buyer|seller|admin),
  "created_at": Date
}
```

#### Products Collection
```javascript
{
  "_id": ObjectId,
  "seller_id": ObjectId,
  "name": String,
  "description": String,
  "price": Number,
  "stock": Number,
  "category": String,
  "created_at": Date
}
```

#### Orders Collection
```javascript
{
  "_id": ObjectId,
  "buyer_id": ObjectId,
  "product_list": [{
    "product_id": ObjectId,
    "quantity": Number,
    "price": Number
  }],
  "total_amount": Number,
  "status": String (placed|completed|cancelled),
  "timestamp": Date
}
```

#### Inventory Logs Collection
```javascript
{
  "_id": ObjectId,
  "product_id": ObjectId,
  "change_type": String (restock|purchase|adjustment),
  "old_stock": Number,
  "new_stock": Number,
  "reason": String,
  "timestamp": Date
}
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile

### Products
- `GET /api/products/` - Get all products (with filters)
- `POST /api/products/` - Create product (seller/admin)
- `PUT /api/products/:id` - Update product (seller/admin)
- `DELETE /api/products/:id` - Delete product (seller/admin)
- `GET /api/products/my-products` - Get seller's products
- `GET /api/products/categories` - Get all categories

### Orders
- `POST /api/orders/` - Place order (buyer)
- `GET /api/orders/my-orders` - Get buyer's orders
- `GET /api/orders/seller-orders` - Get seller's orders
- `PUT /api/orders/:id/status` - Update order status

### Admin
- `GET /api/admin/users` - Get all users
- `GET /api/admin/products` - Get all products
- `GET /api/admin/dashboard` - Get dashboard statistics
- `DELETE /api/admin/users/:id` - Delete user
- `PUT /api/admin/products/:id/disable` - Disable product

## 🧪 Testing Distributed Features

### Fault Tolerance Testing
1. Start multiple backend nodes
2. Kill one node during operation
3. Verify system continues functioning
4. Test MongoDB replica set failover

### Load Testing
1. Use multiple browser tabs/windows
2. Simulate concurrent orders
3. Monitor real-time updates
4. Test stock consistency

### Demo Accounts
- **Buyer**: buyer@demo.com / demo123
- **Seller**: seller@demo.com / demo123
- **Admin**: admin@demo.com / demo123

## 📈 NoSQL Database Features

### Complex Queries Implemented
1. **Top-selling products** with aggregation pipeline
2. **User order history** with date range filtering
3. **Low stock alerts** with threshold-based queries
4. **Sales analytics** with grouping and calculations

### Performance Optimizations
- Compound indexes on frequently queried fields
- Text search indexes for product search
- Proper query optimization with explain plans

### Replica Set Benefits
- **High Availability**: Automatic failover
- **Read Scaling**: Read from secondary nodes
- **Data Redundancy**: Multiple copies of data
- **Disaster Recovery**: Point-in-time recovery

## 🔒 Security Features

- **JWT Authentication** with role-based access
- **Password hashing** using bcrypt
- **Input validation** and sanitization
- **CORS configuration** for cross-origin requests
- **Rate limiting** (can be implemented)

## 📱 Responsive Design

- **Mobile-first** approach
- **Breakpoints**: Mobile (<768px), Tablet (768-1024px), Desktop (>1024px)
- **Touch-friendly** interface elements
- **Optimized** for various screen sizes

## 🚀 Deployment Options

### Local Development
- Direct Python/Node.js execution
- MongoDB local instance

### Docker Compose
- Multi-container setup
- Load balancer with NGINX
- MongoDB replica set

### Cloud Deployment
- Heroku/Render for backend
- Vercel/Netlify for frontend
- MongoDB Atlas for database

## 📚 Educational Value

### Distributed Systems Concepts
- **Load balancing** with NGINX
- **Horizontal scaling** with multiple app instances
- **Fault tolerance** and failover mechanisms
- **Real-time communication** with WebSockets
- **Consistency models** in distributed databases

### NoSQL Database Concepts
- **Document-oriented** data modeling
- **Replica sets** and sharding concepts
- **Aggregation pipelines** for complex queries
- **Index optimization** strategies
- **ACID properties** in MongoDB

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is created for educational purposes as part of university coursework in Distributed Systems and NoSQL Databases.

## 🆘 Troubleshooting

### Common Issues
1. **MongoDB connection errors**: Check replica set configuration
2. **CORS issues**: Verify frontend/backend URLs
3. **WebSocket connection failures**: Check firewall settings
4. **Authentication errors**: Verify JWT secret key

### Performance Tips
1. Use proper database indexes
2. Implement query result caching
3. Optimize WebSocket event handling
4. Monitor memory usage in production

---

**Built with ❤️ for learning Distributed Systems and NoSQL Databases**