import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { slotsApi, SlotUpdate } from '../api/slots'
import { ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'

export default function SlotEditPage() {
  const navigate = useNavigate()
  const { id: cafeIdParam, slotId } = useParams<{ id: string; slotId: string }>()
  const cafeId = cafeIdParam ? Number(cafeIdParam) : null
  const slotIdNum = slotId ? Number(slotId) : null

  const [startTime, setStartTime] = useState<string>('09:00')
  const [endTime, setEndTime] = useState<string>('10:00')
  const [active, setActive] = useState<boolean>(true)
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)

  useEffect(() => {
    if (cafeId && slotIdNum) {
      loadSlot()
    }
  }, [cafeId, slotIdNum])

  const loadSlot = async () => {
    if (!cafeId || !slotIdNum) return
    setFetching(true)
    try {
      const slot = await slotsApi.getSlot(cafeId, slotIdNum)
      // Преобразуем время из формата "HH:mm:ss" в "HH:mm" для input type="time"
      const startTimeStr = slot.start_time.substring(0, 5) // Берем только HH:mm
      const endTimeStr = slot.end_time.substring(0, 5)
      setStartTime(startTimeStr)
      setEndTime(endTimeStr)
      setActive(slot.active)
    } catch (error: any) {
      toast.error('Ошибка загрузки данных слота')
      navigate(`/cafes/${cafeId}`)
    } finally {
      setFetching(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!cafeId || !slotIdNum) {
      toast.error('ID кафе или слота не указан')
      return
    }

    // Basic time validation
    const start = new Date(`2000-01-01T${startTime}:00`)
    const end = new Date(`2000-01-01T${endTime}:00`)

    if (start >= end) {
      toast.error('Время начала должно быть раньше времени окончания')
      return
    }

    setLoading(true)
    try {
      const slotData: SlotUpdate = {
        start_time: `${startTime}:00`, // Ensure HH:mm:ss format
        end_time: `${endTime}:00`,     // Ensure HH:mm:ss format
        active: active,
      }
      await slotsApi.updateSlot(cafeId, slotIdNum, slotData)
      toast.success('Временной слот успешно обновлен!')
      navigate(`/cafes/${cafeId}`)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка обновления слота')
    } finally {
      setLoading(false)
    }
  }

  if (fetching) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8 max-w-3xl mx-auto">
      <button
        onClick={() => navigate(`/cafes/${cafeId}`)}
        className="text-primary-600 hover:text-primary-700 mb-6 inline-flex items-center"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Назад к кафе
      </button>

      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Редактировать временной слот</h1>
        <p className="mt-2 text-gray-600">Слот #{slotIdNum} в кафе ID: {cafeId}</p>
      </div>

      <form onSubmit={handleSubmit} className="card space-y-6">
        <div>
          <label htmlFor="start_time" className="block text-sm font-medium text-gray-700 mb-2">
            Время начала <span className="text-red-500">*</span>
          </label>
          <input
            type="time"
            id="start_time"
            name="start_time"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            required
            className="input"
          />
        </div>

        <div>
          <label htmlFor="end_time" className="block text-sm font-medium text-gray-700 mb-2">
            Время окончания <span className="text-red-500">*</span>
          </label>
          <input
            type="time"
            id="end_time"
            name="end_time"
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
            required
            className="input"
          />
        </div>

        <div>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={active}
              onChange={(e) => setActive(e.target.checked)}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm font-medium text-gray-700">Активен</span>
          </label>
          <p className="text-xs text-gray-500 mt-1">
            Неактивные слоты не будут отображаться для бронирования
          </p>
        </div>

        <div className="flex space-x-4">
          <button
            type="button"
            onClick={() => navigate(`/cafes/${cafeId}`)}
            className="btn btn-secondary flex-1"
            disabled={loading}
          >
            Отмена
          </button>
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary flex-1"
          >
            {loading ? 'Сохранение...' : 'Сохранить изменения'}
          </button>
        </div>
      </form>
    </div>
  )
}

