import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Cafes from './pages/Cafes'
import CafeDetail from './pages/CafeDetail'
import CafeCreate from './pages/CafeCreate'
import TableCreate from './pages/TableCreate'
import TableEdit from './pages/TableEdit'
import SlotCreate from './pages/SlotCreate'
import SlotEdit from './pages/SlotEdit'
import Bookings from './pages/Bookings'
import BookingCreate from './pages/BookingCreate'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Toaster position="top-right" />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/cafes" replace />} />
            <Route path="cafes" element={<Cafes />} />
            <Route path="cafes/create" element={<CafeCreate />} />
            <Route path="cafes/:id" element={<CafeDetail />} />
            <Route path="cafes/:id/tables/create" element={<TableCreate />} />
            <Route path="cafes/:id/tables/:tableId/edit" element={<TableEdit />} />
            <Route path="cafes/:id/slots/create" element={<SlotCreate />} />
            <Route path="cafes/:id/slots/:slotId/edit" element={<SlotEdit />} />
            <Route path="bookings" element={<Bookings />} />
            <Route path="bookings/create" element={<BookingCreate />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App

