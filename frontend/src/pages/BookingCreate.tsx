import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { cafesApi, Cafe } from '../api/cafes'
import { tablesApi, Table } from '../api/tables'
import { slotsApi, Slot } from '../api/slots'
import { bookingsApi, BookingCreate as BookingCreateData } from '../api/bookings'
import { Calendar, Users, Clock, ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'
import { format } from 'date-fns'

export default function BookingCreatePage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const cafeIdParam = searchParams.get('cafe_id')

  const [cafe, setCafe] = useState<Cafe | null>(null)
  const [tables, setTables] = useState<Table[]>([])
  const [slots, setSlots] = useState<Slot[]>([])
  const [selectedTable, setSelectedTable] = useState<number | null>(null)
  const [selectedSlot, setSelectedSlot] = useState<number | null>(null)
  const [selectedDate, setSelectedDate] = useState<string>(
    format(new Date(), 'yyyy-MM-dd')
  )
  const [note, setNote] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    const cafeId = cafeIdParam ? Number(cafeIdParam) : null
    if (cafeId) {
      loadData(cafeId)
    } else {
      setLoading(false)
    }
  }, [cafeIdParam])

  const loadData = async (cafeId: number, date?: string) => {
    try {
      const cafeData = await cafesApi.getCafe(cafeId)
      setCafe(cafeData)
      
      // Загружаем сначала слоты, потом столы с учетом выбранного слота
      const slotsData = await slotsApi.getSlots(cafeId, date, selectedTable || undefined)
      setSlots(slotsData)
      if (slotsData.length > 0 && !selectedSlot) setSelectedSlot(slotsData[0].id)
      
      // Загружаем столы с учетом выбранной даты и слота
      const tablesData = await tablesApi.getTables(cafeId, date, selectedSlot || undefined)
      setTables(tablesData)
      if (tablesData.length > 0 && !selectedTable) setSelectedTable(tablesData[0].id)
    } catch (error: any) {
      toast.error('Ошибка загрузки данных')
    } finally {
      setLoading(false)
    }
  }
  
  useEffect(() => {
    const cafeId = cafeIdParam ? Number(cafeIdParam) : null
    if (cafeId) {
      loadData(cafeId, selectedDate)
    } else {
      setLoading(false)
    }
  }, [cafeIdParam])
  
  // Перезагружаем доступные столы/слоты при изменении даты или выбранного стола/слота
  useEffect(() => {
    if (cafeIdParam && selectedDate) {
      const cafeId = Number(cafeIdParam)
      const loadAvailable = async () => {
        try {
          // Загружаем слоты с учетом выбранного стола
          const slotsData = await slotsApi.getSlots(cafeId, selectedDate, selectedTable || undefined)
          setSlots(slotsData)
          if (slotsData.length > 0 && !slotsData.find(s => s.id === selectedSlot)) {
            setSelectedSlot(slotsData[0].id)
          }
          
          // Загружаем столы с учетом выбранного слота
          const tablesData = await tablesApi.getTables(cafeId, selectedDate, selectedSlot || undefined)
          setTables(tablesData)
          if (tablesData.length > 0 && !tablesData.find(t => t.id === selectedTable)) {
            setSelectedTable(tablesData[0].id)
          }
        } catch (error: any) {
          toast.error('Ошибка загрузки доступных столов/слотов')
        }
      }
      loadAvailable()
    }
  }, [selectedDate, selectedTable, selectedSlot, cafeIdParam])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!selectedTable || !selectedSlot || !cafe) {
      toast.error('Заполните все поля')
      return
    }

    setSubmitting(true)
    try {
      const bookingData: BookingCreateData = {
        cafe_id: cafe.id,
        table_id: selectedTable,
        slot_id: selectedSlot,
        date: selectedDate,
        note: note || undefined,
      }
      
      await bookingsApi.createBooking(bookingData)
      toast.success('Бронирование создано успешно!')
      navigate('/bookings')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка создания бронирования')
    } finally {
      setSubmitting(false)
    }
  }

  const formatTime = (time: string) => {
    return format(new Date(`2000-01-01T${time}`), 'HH:mm')
  }

  const minDate = format(new Date(), 'yyyy-MM-dd')

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
        <button
          onClick={() => navigate('/cafes')}
          className="text-primary-600 hover:underline mt-4"
        >
          Вернуться к списку кафе
        </button>
      </div>
    )
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8 max-w-3xl mx-auto">
      <button
        onClick={() => navigate(-1)}
        className="text-primary-600 hover:text-primary-700 mb-6 inline-flex items-center"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Назад
      </button>

      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Новое бронирование</h1>
        <p className="mt-2 text-gray-600">{cafe.name}</p>
      </div>

      <form onSubmit={handleSubmit} className="card space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Calendar className="h-4 w-4 inline mr-2" />
            Дата
          </label>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            min={minDate}
            required
            className="input"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Users className="h-4 w-4 inline mr-2" />
            Стол
          </label>
          {tables.length === 0 ? (
            <div className="input bg-yellow-50 border-yellow-200">
              <p className="text-yellow-800 text-sm">
                В этом кафе пока нет столов. Обратитесь к администратору для добавления столов.
              </p>
            </div>
          ) : (
            <select
              value={selectedTable || ''}
              onChange={(e) => setSelectedTable(Number(e.target.value))}
              required
              className="input"
            >
              <option value="">Выберите стол</option>
              {tables.map((table) => (
                <option key={table.id} value={table.id}>
                  Стол #{table.id} ({table.seats_count} {table.seats_count === 1 ? 'место' : 'мест'})
                  {table.description && ` - ${table.description}`}
                </option>
              ))}
            </select>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Clock className="h-4 w-4 inline mr-2" />
            Время
          </label>
          {slots.length === 0 ? (
            <div className="input bg-yellow-50 border-yellow-200">
              <p className="text-yellow-800 text-sm">
                В этом кафе пока нет временных слотов. Обратитесь к администратору для добавления слотов.
              </p>
            </div>
          ) : (
            <>
              <select
                value={selectedSlot || ''}
                onChange={(e) => {
                  const newSlotId = Number(e.target.value)
                  setSelectedSlot(newSlotId)
                }}
                required
                className="input"
              >
                <option value="">Выберите время</option>
                {slots.map((slot) => (
                  <option key={slot.id} value={slot.id}>
                    {formatTime(slot.start_time)} - {formatTime(slot.end_time)}
                  </option>
                ))}
              </select>
              {selectedDate && slots.length === 0 && (
                <p className="text-sm text-yellow-600 mt-1">
                  На выбранную дату и стол нет доступного времени
                </p>
              )}
            </>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Примечание (необязательно)
          </label>
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            rows={3}
            className="input"
            placeholder="Дополнительная информация..."
          />
        </div>

        <div className="flex space-x-4">
          <button
            type="submit"
            disabled={submitting || tables.length === 0 || slots.length === 0}
            className="btn btn-primary flex-1"
          >
            {submitting ? 'Создание...' : 'Забронировать'}
          </button>
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="btn btn-secondary"
          >
            Отмена
          </button>
        </div>
      </form>
    </div>
  )
}

