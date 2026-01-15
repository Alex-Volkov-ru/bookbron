import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { slotsApi, SlotCreate } from '../api/slots'
import { ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'

export default function SlotCreatePage() {
  const { id: cafeId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  
  const [startTime, setStartTime] = useState<string>('09:00')
  const [endTime, setEndTime] = useState<string>('10:00')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!cafeId) {
      toast.error('ID кафе не указан')
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
      const slotData: SlotCreate = {
        start_time: `${startTime}:00`, // Ensure HH:mm:ss format
        end_time: `${endTime}:00`,     // Ensure HH:mm:ss format
      }
      await slotsApi.createSlot(Number(cafeId), slotData)
      toast.success('Временной слот создан успешно!')
      navigate(`/cafes/${cafeId}`)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка создания слота')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8 max-w-3xl mx-auto">
      <button
        onClick={() => navigate(`/cafes/${cafeId}`)}
        className="text-primary-600 hover:text-primary-700 mb-6 inline-flex items-center"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Назад
      </button>

      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Создание временного слота</h1>
        <p className="mt-2 text-gray-600">Добавьте новый временной слот для кафе</p>
      </div>

      <form onSubmit={handleSubmit} className="card space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Время начала <span className="text-red-500">*</span>
          </label>
          <input
            type="time"
            required
            className="input"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Время окончания <span className="text-red-500">*</span>
          </label>
          <input
            type="time"
            required
            className="input"
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
          />
        </div>

        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate(`/cafes/${cafeId}`)}
            className="btn btn-secondary"
            disabled={loading}
          >
            Отмена
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Создание...' : 'Создать слот'}
          </button>
        </div>
      </form>
    </div>
  )
}

