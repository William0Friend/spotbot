import { Link, useLocation } from 'react-router-dom'
import { Search, History, Home, LogIn, UserPlus, LogOut } from 'lucide-react'
import useAuthStore from '../store/authStore'

export default function Layout({ children }) {
  const location = useLocation()
  const { isAuthenticated, logout } = useAuthStore()
  
  const isActive = (path) => location.pathname === path
  
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                <Search className="text-white" size={24} />
              </div>
              <span className="text-2xl font-bold text-gray-900">SpotBot</span>
            </Link>
            
            <nav className="flex items-center space-x-6">
              <Link
                to="/"
                className={`flex items-center space-x-1 ${
                  isActive('/') ? 'text-primary-600' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Home size={20} />
                <span>Home</span>
              </Link>
              
              <Link
                to="/detect"
                className={`flex items-center space-x-1 ${
                  isActive('/detect') ? 'text-primary-600' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Search size={20} />
                <span>Detect</span>
              </Link>
              
              <Link
                to="/history"
                className={`flex items-center space-x-1 ${
                  isActive('/history') ? 'text-primary-600' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <History size={20} />
                <span>History</span>
              </Link>
              
              {isAuthenticated ? (
                <button
                  onClick={logout}
                  className="flex items-center space-x-1 text-gray-600 hover:text-gray-900"
                >
                  <LogOut size={20} />
                  <span>Logout</span>
                </button>
              ) : (
                <>
                  <Link
                    to="/login"
                    className={`flex items-center space-x-1 ${
                      isActive('/login') ? 'text-primary-600' : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <LogIn size={20} />
                    <span>Login</span>
                  </Link>
                  
                  <Link
                    to="/register"
                    className="btn-primary flex items-center space-x-1"
                  >
                    <UserPlus size={20} />
                    <span>Sign Up</span>
                  </Link>
                </>
              )}
            </nav>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>
      
      {/* Footer */}
      <footer className="bg-gray-100 border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">SpotBot</h3>
              <p className="text-gray-600 text-sm">
                AI content detection platform. Identify AI-generated content with confidence.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Product</h3>
              <ul className="space-y-2 text-sm">
                <li><Link to="/detect" className="text-gray-600 hover:text-gray-900">Detection</Link></li>
                <li><Link to="/history" className="text-gray-600 hover:text-gray-900">History</Link></li>
                <li><a href="http://localhost:8000/docs" className="text-gray-600 hover:text-gray-900">API Docs</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Support</h3>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="text-gray-600 hover:text-gray-900">Documentation</a></li>
                <li><a href="#" className="text-gray-600 hover:text-gray-900">Contact</a></li>
                <li><a href="#" className="text-gray-600 hover:text-gray-900">GitHub</a></li>
              </ul>
            </div>
          </div>
          
          <div className="mt-8 pt-8 border-t border-gray-200 text-center text-sm text-gray-600">
            © 2024 SpotBot. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}
