import React from 'react';
import { ShoppingCart, User, Settings, LogOut, Store, BarChart3 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

interface NavbarProps {
  currentView: string;
  setCurrentView: (view: string) => void;
}

const Navbar: React.FC<NavbarProps> = ({ currentView, setCurrentView }) => {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-white shadow-lg fixed top-0 left-0 right-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <Store className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">
                DistroMart
              </span>
            </div>
            
            <div className="ml-10 flex items-baseline space-x-4">
              <button
                onClick={() => setCurrentView('catalog')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentView === 'catalog'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:text-blue-600'
                }`}
              >
                Products
              </button>
              
              <button
                onClick={() => setCurrentView('dashboard')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentView === 'dashboard'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:text-blue-600'
                }`}
              >
                {user?.role === 'buyer' ? 'My Orders' : 
                 user?.role === 'seller' ? 'My Store' : 'Admin Panel'}
              </button>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1">
                <User className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-700">{user?.name}</span>
              </div>
              
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                user?.role === 'admin' ? 'bg-red-100 text-red-800' :
                user?.role === 'seller' ? 'bg-green-100 text-green-800' :
                'bg-blue-100 text-blue-800'
              }`}>
                {user?.role}
              </span>
            </div>

            <button
              onClick={logout}
              className="flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-red-600 hover:bg-red-50 transition-colors"
            >
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar