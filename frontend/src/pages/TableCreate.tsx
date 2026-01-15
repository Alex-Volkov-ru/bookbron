import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { tablesApi, TableCreate } from '../api/tables'
import { ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'

export default function TableCreatePage() {
  const { id: cafeId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  
  const [seatsCount, setSeatsCount] = useState<number>(2)
  const [description, setDescription] = useState<string>('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!cafeId) {
      toast.error('ID кафе не указан')
      return
    }

    setLoading(true)
    try {
      const tableData: TableCreate = {
        seats_count: seatsCount,
        description: description || undefined,
      }
      await tablesApi.createTable(Number(cafeId), tableData)
      toast.success('Стол создан успешно!')
      navigate(`/cafes/${cafeId}`)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка создания стола')
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
        <h1 className="text-3xl font-bold text-gray-900">Создание стола</h1>
        <p className="mt-2 text-gray-600">Добавьте новый стол в кафе</p>
      </div>

      <form onSubmit={handleSubmit} className="card space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Количество мест <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            required
            min={1}
            className="input"
            placeholder="Количество мест"
            value={seatsCount}
            onChange={(e) => setSeatsCount(Number(e.target.value))}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Описание
          </label>
          <textarea
            className="input"
            rows={3}
            placeholder="Описание стола (необязательно)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
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
            {loading ? 'Создание...' : 'Создать стол'}
          </button>
        </div>
      </form>
    </div>
  )
}

