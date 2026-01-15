import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { tablesApi, TableUpdate } from '../api/tables'
import { ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'

export default function TableEditPage() {
  const navigate = useNavigate()
  const { id: cafeIdParam, tableId } = useParams<{ id: string; tableId: string }>()
  const cafeId = cafeIdParam ? Number(cafeIdParam) : null
  const tableIdNum = tableId ? Number(tableId) : null

  const [seatsCount, setSeatsCount] = useState<number>(1)
  const [description, setDescription] = useState<string>('')
  const [active, setActive] = useState<boolean>(true)
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)

  useEffect(() => {
    if (cafeId && tableIdNum) {
      loadTable()
    }
  }, [cafeId, tableIdNum])

  const loadTable = async () => {
    if (!cafeId || !tableIdNum) return
    setFetching(true)
    try {
      const table = await tablesApi.getTable(cafeId, tableIdNum)
      setSeatsCount(table.seats_count)
      setDescription(table.description || '')
      setActive(table.active)
    } catch (error: any) {
      toast.error('Ошибка загрузки данных стола')
      navigate(`/cafes/${cafeId}`)
    } finally {
      setFetching(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!cafeId || !tableIdNum) {
      toast.error('ID кафе или стола не указан')
      return
    }
    if (seatsCount <= 0) {
      toast.error('Количество мест должно быть больше 0')
      return
    }

    setLoading(true)
    try {
      const tableData: TableUpdate = {
        seats_count: seatsCount,
        description: description || undefined,
        active: active,
      }
      await tablesApi.updateTable(cafeId, tableIdNum, tableData)
      toast.success('Стол успешно обновлен!')
      navigate(`/cafes/${cafeId}`)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка обновления стола')
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
        <h1 className="text-3xl font-bold text-gray-900">Редактировать стол</h1>
        <p className="mt-2 text-gray-600">Стол #{tableIdNum} в кафе ID: {cafeId}</p>
      </div>

      <form onSubmit={handleSubmit} className="card space-y-6">
        <div>
          <label htmlFor="seats_count" className="block text-sm font-medium text-gray-700 mb-2">
            Количество мест <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            id="seats_count"
            name="seats_count"
            value={seatsCount}
            onChange={(e) => setSeatsCount(Number(e.target.value))}
            min={1}
            required
            className="input"
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
            Описание (необязательно)
          </label>
          <textarea
            id="description"
            name="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="input"
            placeholder="Например: Стол у окна, VIP-зона"
          ></textarea>
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
            Неактивные столы не будут отображаться для бронирования
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
            disabled={loading || seatsCount <= 0}
            className="btn btn-primary flex-1"
          >
            {loading ? 'Сохранение...' : 'Сохранить изменения'}
          </button>
        </div>
      </form>
    </div>
  )
}

