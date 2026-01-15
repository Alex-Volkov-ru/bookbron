import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { bookingsApi, Booking } from '../api/bookings'
import { Calendar, Clock, MapPin, X } from 'lucide-react'
import toast from 'react-hot-toast'
import { format } from 'date-fns'

export default function Bookings() {
  const [bookings, setBookings] = useState<Booking[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadBookings()
  }, [])

  const loadBookings = async () => {
    try {
      const data = await bookingsApi.getBookings()
      setBookings(data)
    } catch (error: any) {
      toast.error('Ошибка загрузки бронирований')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async (id: number) => {
    if (!confirm('Вы уверены, что хотите отменить бронирование?')) {
      return
    }

    try {
      await bookingsApi.cancelBooking(id)
      toast.success('Бронирование отменено')
      loadBookings()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка отмены бронирования')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-100 text-green-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      case 'completed':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'Подтверждено'
      case 'pending':
        return 'Ожидает подтверждения'
      case 'cancelled':
        return 'Отменено'
      case 'completed':
        return 'Завершено'
      default:
        return status
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Мои бронирования</h1>
          <p className="mt-2 text-gray-600">Управление вашими бронированиями</p>
        </div>
        <Link to="/cafes" className="btn btn-primary">
          <Calendar className="h-5 w-5 mr-2" />
          Новое бронирование
        </Link>
      </div>

      {bookings.length === 0 ? (
        <div className="text-center py-12">
          <Calendar className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 text-lg mb-4">У вас пока нет бронирований</p>
          <Link to="/cafes" className="btn btn-primary">
            Забронировать стол
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {bookings.map((booking) => (
            <div key={booking.id} className="card">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-semibold">
                      Бронирование #{booking.id}
                    </h3>
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
                        booking.status
                      )}`}
                    >
                      {getStatusText(booking.status)}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div className="flex items-center text-gray-700">
                      <Calendar className="h-5 w-5 mr-2 text-primary-600" />
                      <span>
                        {format(new Date(booking.date), 'd MMMM yyyy')}
                      </span>
                    </div>
                    <div className="flex items-center text-gray-700">
                      <Clock className="h-5 w-5 mr-2 text-primary-600" />
                      <span>Слот #{booking.slot_id}</span>
                    </div>
                    <div className="flex items-center text-gray-700">
                      <MapPin className="h-5 w-5 mr-2 text-primary-600" />
                      <span>Стол #{booking.table_id}</span>
                    </div>
                  </div>

                  {booking.note && (
                    <div className="mb-4">
                      <p className="text-sm text-gray-600">
                        <span className="font-medium">Примечание:</span> {booking.note}
                      </p>
                    </div>
                  )}

                  {booking.dishes && booking.dishes.length > 0 && (
                    <div className="mb-4">
                      <p className="text-sm font-medium text-gray-700 mb-2">Блюда:</p>
                      <ul className="space-y-1">
                        {booking.dishes.map((dish) => (
                          <li key={dish.id} className="text-sm text-gray-600">
                            {dish.dish_name} x{dish.quantity} - {dish.price}₽
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {booking.status !== 'cancelled' && booking.status !== 'completed' && (
                  <div className="flex space-x-2 ml-4">
                    <button
                      onClick={() => handleCancel(booking.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Отменить"
                    >
                      <X className="h-5 w-5" />
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

