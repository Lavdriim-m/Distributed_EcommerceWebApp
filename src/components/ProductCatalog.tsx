import React, { useState, useEffect } from 'react';
import { Search, Filter, Plus, Minus, ShoppingCart, AlertTriangle } from 'lucide-react';
import { Socket } from 'socket.io-client';
import { useAuth } from '../contexts/AuthContext';
import { useNotifications } from '../contexts/NotificationContext';

interface Product {
  _id: { $oid: string };
  name: string;
  description: string;
  price: number;
  stock: number;
  category: string;
  seller_id: { $oid: string };
}

interface ProductCatalogProps {
  socket: Socket | null;
}

const ProductCatalog: React.FC<ProductCatalogProps> = ({ socket }) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<{ [key: string]: number }>({});
  const [categories, setCategories] = useState<string[]>([]);
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    minPrice: '',
    maxPrice: '',
    inStock: false
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isPlacingOrder, setIsPlacingOrder] = useState(false);
  
  const { token, user } = useAuth();
  const { addNotification } = useNotifications();

  useEffect(() => {
    fetchProducts();
    fetchCategories();
  }, []);

  useEffect(() => {
    // Listen for real-time stock updates
    if (socket) {
      socket.on('stock_update', (data) => {
        setProducts(prev => prev.map(product => 
          product._id.$oid === data.product_id 
            ? { ...product, stock: data.new_stock }
            : product
        ));
        
        addNotification({
          type: 'info',
          title: 'Stock Update',
          message: `${data.product_name} stock updated to ${data.new_stock}`
        });
      });

      return () => {
        socket.off('stock_update');
      };
    }
  }, [socket, addNotification]);

  useEffect(() => {
    applyFilters();
  }, [products, filters]);

  const fetchProducts = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost/api/products/');
      const data = await response.json();
      
      if (response.ok) {
        setProducts(data.products);
      }
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch('http://localhost/api/products/categories');
      const data = await response.json();
      
      if (response.ok) {
        setCategories(data.categories);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const applyFilters = () => {
    let filtered = products;

    if (filters.search) {
      filtered = filtered.filter(product =>
        product.name.toLowerCase().includes(filters.search.toLowerCase()) ||
        product.description.toLowerCase().includes(filters.search.toLowerCase())
      );
    }

    if (filters.category) {
      filtered = filtered.filter(product => product.category === filters.category);
    }

    if (filters.minPrice) {
      filtered = filtered.filter(product => product.price >= parseFloat(filters.minPrice));
    }

    if (filters.maxPrice) {
      filtered = filtered.filter(product => product.price <= parseFloat(filters.maxPrice));
    }

    if (filters.inStock) {
      filtered = filtered.filter(product => product.stock > 0);
    }

    setFilteredProducts(filtered);
  };

  const updateCart = (productId: string, quantity: number) => {
    setCart(prev => {
      const newCart = { ...prev };
      if (quantity <= 0) {
        delete newCart[productId];
      } else {
        newCart[productId] = quantity;
      }
      return newCart;
    });
  };

  const getCartTotal = () => {
    return Object.entries(cart).reduce((total, [productId, quantity]) => {
      const product = products.find(p => p._id.$oid === productId);
      return total + (product ? product.price * quantity : 0);
    }, 0);
  };

  const getCartItemCount = () => {
    return Object.values(cart).reduce((total, quantity) => total + quantity, 0);
  };

  const placeOrder = async () => {
    if (!token || user?.role !== 'buyer') {
      addNotification({
        type: 'error',
        title: 'Authentication Required',
        message: 'Please login as a buyer to place orders'
      });
      return;
    }

    if (Object.keys(cart).length === 0) {
      addNotification({
        type: 'warning',
        title: 'Empty Cart',
        message: 'Please add items to cart before placing order'
      });
      return;
    }

    try {
      setIsPlacingOrder(true);
      
      const orderProducts = Object.entries(cart).map(([productId, quantity]) => ({
        product_id: productId,
        quantity
      }));

      const response = await fetch('http://localhost/api/orders/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ products: orderProducts })
      });

      const data = await response.json();

      if (response.ok) {
        setCart({});
        addNotification({
          type: 'success',
          title: 'Order Placed',
          message: `Order placed successfully! Total: $${data.total_amount.toFixed(2)}`
        });
        fetchProducts(); // Refresh products to get updated stock
      } else {
        addNotification({
          type: 'error',
          title: 'Order Failed',
          message: data.error || 'Failed to place order'
        });
      }
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Order Error',
        message: 'An error occurred while placing the order'
      });
    } finally {
      setIsPlacingOrder(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Product Catalog</h1>
        <p className="text-gray-600">Discover amazing products from our distributed marketplace</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search products..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              className="pl-10 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <select
            value={filters.category}
            onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value }))}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Categories</option>
            {categories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
          
          <input
            type="number"
            placeholder="Min Price"
            value={filters.minPrice}
            onChange={(e) => setFilters(prev => ({ ...prev, minPrice: e.target.value }))}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          
          <input
            type="number"
            placeholder="Max Price"
            value={filters.maxPrice}
            onChange={(e) => setFilters(prev => ({ ...prev, maxPrice: e.target.value }))}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={filters.inStock}
              onChange={(e) => setFilters(prev => ({ ...prev, inStock: e.target.checked }))}
              className="rounded text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">In Stock Only</span>
          </label>
        </div>
      </div>

      {/* Cart Summary */}
      {user?.role === 'buyer' && getCartItemCount() > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <ShoppingCart className="h-5 w-5 text-blue-600" />
              <span className="font-medium text-blue-900">
                Cart: {getCartItemCount()} items
              </span>
              <span className="text-blue-700">
                Total: ${getCartTotal().toFixed(2)}
              </span>
            </div>
            <button
              onClick={placeOrder}
              disabled={isPlacingOrder}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium disabled:opacity-50 transition-colors"
            >
              {isPlacingOrder ? 'Placing Order...' : 'Place Order'}
            </button>
          </div>
        </div>
      )}

      {/* Products Grid */}
      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredProducts.map((product) => (
            <div key={product._id.$oid} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 truncate">
                    {product.name}
                  </h3>
                  <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded">
                    {product.category}
                  </span>
                </div>
                
                <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                  {product.description}
                </p>
                
                <div className="flex justify-between items-center mb-4">
                  <span className="text-2xl font-bold text-gray-900">
                    ${product.price.toFixed(2)}
                  </span>
                  <div className={`flex items-center space-x-1 ${
                    product.stock <= 5 ? 'text-red-600' : 'text-green-600'
                  }`}>
                    {product.stock <= 5 && <AlertTriangle className="h-4 w-4" />}
                    <span className="text-sm font-medium">
                      {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
                    </span>
                  </div>
                </div>
                
                {user?.role === 'buyer' && product.stock > 0 && (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => updateCart(product._id.$oid, Math.max(0, (cart[product._id.$oid] || 0) - 1))}
                        className="p-1 rounded-md bg-gray-100 hover:bg-gray-200 transition-colors"
                      >
                        <Minus className="h-4 w-4" />
                      </button>
                      <span className="w-8 text-center font-medium">
                        {cart[product._id.$oid] || 0}
                      </span>
                      <button
                        onClick={() => updateCart(product._id.$oid, Math.min(product.stock, (cart[product._id.$oid] || 0) + 1))}
                        className="p-1 rounded-md bg-gray-100 hover:bg-gray-200 transition-colors"
                      >
                        <Plus className="h-4 w-4" />
                      </button>
                    </div>
                    <span className="text-sm text-gray-500">
                      Max: {product.stock}
                    </span>
                  </div>
                )}
                
                {user?.role === 'buyer' && product.stock === 0 && (
                  <div className="text-center py-2 text-red-600 font-medium">
                    Out of Stock
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {filteredProducts.length === 0 && !isLoading && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No products found matching your criteria.</p>
        </div>
      )}
    </div>
  );
};

export default ProductCatalog