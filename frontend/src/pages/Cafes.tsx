import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { cafesApi, Cafe } from '../api/cafes'
import { MapPin, Phone, ArrowRight, Plus, Users } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../contexts/AuthContext'

export default function Cafes() {
  const [cafes, setCafes] = useState<Cafe[]>([])
  const [loading, setLoading] = useState(true)
  const { user } = useAuth()
  const navigate = useNavigate()
  
  const isAdmin = user?.role === 'admin'

  useEffect(() => {
    loadCafes()
  }, [])

  const loadCafes = async () => {
    try {
      const data = await cafesApi.getCafes()
      setCafes(data)
    } catch (error: any) {
      toast.error('Ошибка загрузки кафе')
    } finally {
      setLoading(false)
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
          <h1 className="text-3xl font-bold text-gray-900">Кафе</h1>
          <p className="mt-2 text-gray-600">Выберите кафе для бронирования</p>
        </div>
        {isAdmin && (
          <button
            onClick={() => navigate('/cafes/create')}
            className="btn btn-primary"
          >
            <Plus className="h-5 w-5 mr-2" />
            Создать кафе
          </button>
        )}
      </div>

      {cafes.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">Кафе пока нет</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cafes.map((cafe) => (
            <Link
              key={cafe.id}
              to={`/cafes/${cafe.id}`}
              className="card hover:shadow-lg transition-shadow duration-200"
            >
              {cafe.photo && (
                <div className="w-full h-48 bg-gray-200 rounded-lg mb-4 overflow-hidden">
                  <img
                    src={`http://localhost:8000/media/${cafe.photo}`}
                    alt={cafe.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none'
                    }}
                  />
                </div>
              )}
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xl font-semibold text-gray-900">
                  {cafe.name}
                </h3>
                {user?.role === 'manager' && cafe.managers?.some(m => m.id === user.id) && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    <Users className="h-3 w-3 mr-1" />
                    Ваше кафе
                  </span>
                )}
              </div>
              {cafe.description && (
                <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                  {cafe.description}
                </p>
              )}
              <div className="space-y-2 text-sm text-gray-500">
                <div className="flex items-center">
                  <MapPin className="h-4 w-4 mr-2" />
                  <span>{cafe.address}</span>
                </div>
                {cafe.phone && (
                  <div className="flex items-center">
                    <Phone className="h-4 w-4 mr-2" />
                    <span>{cafe.phone}</span>
                  </div>
                )}
              </div>
              <div className="mt-4 flex items-center text-primary-600 font-medium">
                <span>Забронировать</span>
                <ArrowRight className="h-4 w-4 ml-2" />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

