import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { cafesApi, Cafe } from '../api/cafes'
import { tablesApi, Table } from '../api/tables'
import { slotsApi, Slot } from '../api/slots'
import { MapPin, Phone, Calendar, Users, Plus, Edit, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { format } from 'date-fns'
import { useAuth } from '../contexts/AuthContext'

export default function CafeDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [cafe, setCafe] = useState<Cafe | null>(null)
  const [tables, setTables] = useState<Table[]>([])
  const [slots, setSlots] = useState<Slot[]>([])
  const [loading, setLoading] = useState(true)
  
  const isAdmin = user?.role === 'admin'
  const isManager = user?.role === 'manager'
  const canManage = isAdmin || isManager

  useEffect(() => {
    if (id) {
      loadData()
    }
  }, [id])

  const loadData = async () => {
    if (!id) return
    try {
      const [cafeData, tablesData, slotsData] = await Promise.all([
        cafesApi.getCafe(Number(id)),
        tablesApi.getTables(Number(id)),
        slotsApi.getSlots(Number(id)),
      ])
      setCafe(cafeData)
      setTables(tablesData)
      setSlots(slotsData)
    } catch (error: any) {
      toast.error('Ошибка загрузки данных')
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

  if (!cafe) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Кафе не найдено</p>
        <Link to="/cafes" className="text-primary-600 hover:underline mt-4 inline-block">
          Вернуться к списку кафе
        </Link>
      </div>
    )
  }

  const formatTime = (time: string) => {
    return format(new Date(`2000-01-01T${time}`), 'HH:mm')
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <Link
        to="/cafes"
        className="text-primary-600 hover:text-primary-700 mb-4 inline-block"
      >
        ← Назад к списку кафе
      </Link>

      <div className="card mb-6">
        <div className="flex flex-col md:flex-row gap-6">
          {cafe.photo && (
            <div className="w-full md:w-1/3 h-64 bg-gray-200 rounded-lg overflow-hidden">
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
          <div className="flex-1">
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-3xl font-bold text-gray-900">{cafe.name}</h1>
              {isManager && cafe.managers?.some(m => m.id === user?.id) && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  <Users className="h-3 w-3 mr-1" />
                  Вы менеджер этого кафе
                </span>
              )}
            </div>
            {cafe.description && (
              <p className="text-gray-600 mb-4">{cafe.description}</p>
            )}
            <div className="space-y-2">
              <div className="flex items-center text-gray-700">
                <MapPin className="h-5 w-5 mr-2 text-primary-600" />
                <span>{cafe.address}</span>
              </div>
              {cafe.phone && (
                <div className="flex items-center text-gray-700">
                  <Phone className="h-5 w-5 mr-2 text-primary-600" />
                  <span>{cafe.phone}</span>
                </div>
              )}
              {cafe.work_start_time && cafe.work_end_time && (
                <div className="flex items-center text-gray-700">
                  <Calendar className="h-5 w-5 mr-2 text-primary-600" />
                  <span>
                    Рабочее время: {formatTime(cafe.work_start_time)} - {formatTime(cafe.work_end_time)}
                    {cafe.slot_duration_minutes && ` (слоты по ${cafe.slot_duration_minutes} мин)`}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold flex items-center">
              <Users className="h-5 w-5 mr-2 text-primary-600" />
              Столы
            </h2>
            {canManage && (
              <button
                onClick={() => navigate(`/cafes/${id}/tables/create`)}
                className="btn btn-primary btn-sm"
              >
                <Plus className="h-4 w-4 mr-1" />
                Добавить стол
              </button>
            )}
          </div>
          {tables.length === 0 ? (
            <p className="text-gray-500">Столы не найдены</p>
          ) : (
            <div className="space-y-2">
              {tables.map((table) => (
                <div
                  key={table.id}
                  className="p-3 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium">Стол #{table.id}</p>
                      <p className="text-sm text-gray-600">
                        {table.seats_count} {table.seats_count === 1 ? 'место' : 'мест'}
                      </p>
                      {table.description && (
                        <p className="text-sm text-gray-500 mt-1">{table.description}</p>
                      )}
                    </div>
                    {canManage && (
                      <div className="flex space-x-2">
                        <button
                          onClick={() => navigate(`/cafes/${id}/tables/${table.id}/edit`)}
                          className="text-primary-600 hover:text-primary-700"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={async () => {
                            if (confirm('Удалить стол?')) {
                              try {
                                await tablesApi.deleteTable(Number(id), table.id)
                                toast.success('Стол удален')
                                loadData()
                              } catch (error: any) {
                                toast.error(error.response?.data?.detail || 'Ошибка удаления стола')
                              }
                            }
                          }}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold flex items-center">
              <Calendar className="h-5 w-5 mr-2 text-primary-600" />
              Доступное время
            </h2>
            {canManage && (
              <div className="flex space-x-2">
                {cafe.work_start_time && cafe.work_end_time && (
                  <button
                    onClick={async () => {
                      if (confirm(`Сгенерировать слоты автоматически на основе рабочего времени?\n${cafe.work_start_time} - ${cafe.work_end_time}, длительность: ${cafe.slot_duration_minutes || 60} мин`)) {
                        try {
                          await slotsApi.generateSlots(Number(id))
                          toast.success('Временные слоты созданы автоматически!')
                          loadData()
                        } catch (error: any) {
                          toast.error(error.response?.data?.detail || 'Ошибка создания слотов')
                        }
                      }
                    }}
                    className="btn btn-secondary btn-sm"
                    title="Автоматически создать слоты на основе рабочего времени"
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Сгенерировать слоты
                  </button>
                )}
                <button
                  onClick={() => navigate(`/cafes/${id}/slots/create`)}
                  className="btn btn-primary btn-sm"
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Добавить слот
                </button>
              </div>
            )}
          </div>
          {slots.length === 0 ? (
            <p className="text-gray-500">Временные слоты не найдены</p>
          ) : (
            <div className="grid grid-cols-2 gap-2">
              {slots.map((slot) => (
                <div
                  key={slot.id}
                  className="p-3 bg-gray-50 rounded-lg border border-gray-200 text-center relative"
                >
                  <p className="font-medium">
                    {formatTime(slot.start_time)} - {formatTime(slot.end_time)}
                  </p>
                  {canManage && (
                    <div className="absolute top-2 right-2 flex space-x-1">
                      <button
                        onClick={() => navigate(`/cafes/${id}/slots/${slot.id}/edit`)}
                        className="text-primary-600 hover:text-primary-700"
                      >
                        <Edit className="h-3 w-3" />
                      </button>
                      <button
                        onClick={async () => {
                          if (confirm('Удалить слот?')) {
                            try {
                              await slotsApi.deleteSlot(Number(id), slot.id)
                              toast.success('Слот удален')
                              loadData()
                            } catch (error: any) {
                              toast.error(error.response?.data?.detail || 'Ошибка удаления слота')
                            }
                          }
                        }}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="mt-6">
        <Link
          to={`/bookings/create?cafe_id=${cafe.id}`}
          className="btn btn-primary inline-flex items-center"
        >
          <Calendar className="h-5 w-5 mr-2" />
          Забронировать стол
        </Link>
      </div>
    </div>
  )
}

