import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Coffee, Calendar, LogOut, User } from 'lucide-react'

export default function Layout() {
  const { user, logout } = useAuth()
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Coffee className="h-8 w-8 text-primary-600" />
                <span className="ml-2 text-xl font-bold text-gray-900">Бронирование</span>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <Link
                  to="/cafes"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                    isActive('/cafes') || location.pathname.startsWith('/cafes/')
                      ? 'border-primary-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Coffee className="h-4 w-4 mr-2" />
                  Кафе
                </Link>
                <Link
                  to="/bookings"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                    isActive('/bookings') || location.pathname.startsWith('/bookings/')
                      ? 'border-primary-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Calendar className="h-4 w-4 mr-2" />
                  Мои бронирования
                </Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-700">
                <User className="h-4 w-4" />
                <span>{user?.username}</span>
              </div>
              <button
                onClick={logout}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-gray-700 hover:text-gray-900 hover:bg-gray-100"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Выход
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  )
}

