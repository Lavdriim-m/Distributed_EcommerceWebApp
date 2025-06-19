import React, { useState, useEffect } from 'react';
import { Package, Clock, CheckCircle, XCircle } from 'lucide-react';
import { Socket } from 'socket.io-client';
import { useAuth } from '../contexts/AuthContext';

interface Order {
  _id: { $oid: string };
  product_list: Array<{
    product_id: { $oid: string };
    quantity: number;
    price: number;
  }>;
  total_amount: number;
  status: 'placed' | 'completed' | 'cancelled';
  timestamp: { $date: string };
}

interface BuyerDashboardProps {
  socket: Socket | null;
}

const BuyerDashboard: React.FC<BuyerDashboardProps> = ({ socket }) => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { token } = useAuth();

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost/api/orders/my-orders', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setOrders(data.orders);
      }
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'placed':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'cancelled':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Package className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'placed':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">My Orders</h1>
        <p className="text-gray-600">Track your order history and current status</p>
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : orders.length === 0 ? (
        <div className="text-center py-12">
          <Package className="h-16 w-16 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No orders yet</h3>
          <p className="text-gray-600">Start shopping to see your orders here!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <div key={order._id.$oid} className="bg-white rounded-lg shadow-md">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(order.status)}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        Order #{order._id.$oid.slice(-8)}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {formatDate(order.timestamp.$date)}
                      </p>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}>
                      {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                    </span>
                    <p className="text-lg font-bold text-gray-900 mt-1">
                      ${order.total_amount.toFixed(2)}
                    </p>
                  </div>
                </div>
                
                <div className="border-t pt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Order Items:</h4>
                  <div className="space-y-2">
                    {order.product_list.map((item, index) => (
                      <div key={index} className="flex justify-between items-center text-sm">
                        <span className="text-gray-600">
                          Product ID: {item.product_id.$oid.slice(-8)}
                        </span>
                        <span className="text-gray-600">
                          Quantity: {item.quantity} × ${item.price.toFixed(2)}
                        </span>
                        <span className="font-medium">
                          ${(item.quantity * item.price).toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default BuyerDashboard