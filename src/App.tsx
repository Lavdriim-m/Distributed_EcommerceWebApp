import { useState, useEffect, Suspense, lazy } from 'react';
import { io, Socket } from 'socket.io-client';
import Login from './components/Login';
import Register from './components/Register';
import Navbar from './components/Navbar';
import NotificationCenter from './components/NotificationCenter';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { NotificationProvider } from './contexts/NotificationContext';

// Lazy load components
const ProductCatalog = lazy(() => import('./components/ProductCatalog'));
const BuyerDashboard = lazy(() => import('./components/BuyerDashboard'));
const SellerDashboard = lazy(() => import('./components/SellerDashboard'));
const AdminDashboard = lazy(() => import('./components/AdminDashboard'));

function AppContent() {
  const { user, isAuthenticated } = useAuth();
  const [currentView, setCurrentView] = useState('catalog');
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    // Initialize socket connection
    const newSocket = io('http://localhost:5000');
    setSocket(newSocket);

    // Join user-specific room if authenticated
    if (isAuthenticated && user) {
      newSocket.emit('join_user_room', { user_id: user.id });
      
      // Join sellers room if user is a seller
      if (user.role === 'seller') {
        newSocket.emit('join_sellers_room');
      }
    }

    return () => {
      newSocket.close();
    };
  }, [isAuthenticated, user]);

  const renderContent = () => {
    if (!isAuthenticated) {
      return currentView === 'login' ? (
        <Login onSwitchToRegister={() => setCurrentView('register')} />
      ) : (
        <Register onSwitchToLogin={() => setCurrentView('login')} />
      );
    }

    return (
      <Suspense fallback={
        <div className="flex justify-center items-center h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      }>
        {currentView === 'catalog' && <ProductCatalog socket={socket} />}
        {currentView === 'dashboard' && (
          user?.role === 'buyer' ? <BuyerDashboard socket={socket} /> :
          user?.role === 'seller' ? <SellerDashboard socket={socket} /> :
          user?.role === 'admin' ? <AdminDashboard socket={socket} /> : null
        )}
      </Suspense>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {isAuthenticated && (
        <>
          <Navbar 
            currentView={currentView} 
            setCurrentView={setCurrentView} 
          />
          <NotificationCenter socket={socket} />
        </>
      )}
      
      <main className={isAuthenticated ? 'pt-16' : ''}>
        {renderContent()}
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <NotificationProvider>
        <AppContent />
      </NotificationProvider>
    </AuthProvider>
  );
}

export default App;