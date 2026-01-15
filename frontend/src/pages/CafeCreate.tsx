import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { cafesApi, CafeCreate } from '../api/cafes'
import { mediaApi } from '../api/media'
import { usersApi, User } from '../api/users'
import { ArrowLeft, Upload, X, Users } from 'lucide-react'
import toast from 'react-hot-toast'

export default function CafeCreatePage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  
  const [formData, setFormData] = useState<CafeCreate>({
    name: '',
    address: '',
    phone: '',
    description: '',
    photo_id: '',
    managers_id: [],
    work_start_time: '09:00',
    work_end_time: '22:00',
    slot_duration_minutes: 60
  })
  
  const [previewImage, setPreviewImage] = useState<string | null>(null)
  const [availableManagers, setAvailableManagers] = useState<User[]>([])
  const [loadingManagers, setLoadingManagers] = useState(false)
  
  useEffect(() => {
    loadManagers()
  }, [])
  
  const loadManagers = async () => {
    setLoadingManagers(true)
    try {
      const users = await usersApi.getUsers()
      // Фильтруем только пользователей с ролью manager
      const managers = users.filter(u => u.role === 'manager' && u.active)
      setAvailableManagers(managers)
    } catch (error: any) {
      toast.error('Ошибка загрузки списка менеджеров')
    } finally {
      setLoadingManagers(false)
    }
  }
  
  const toggleManager = (managerId: number) => {
    setFormData(prev => {
      const currentIds = prev.managers_id || []
      if (currentIds.includes(managerId)) {
        return { ...prev, managers_id: currentIds.filter(id => id !== managerId) }
      } else {
        return { ...prev, managers_id: [...currentIds, managerId] }
      }
    })
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.type.startsWith('image/')) {
      toast.error('Выберите изображение')
      return
    }
    
    // Превью
    const reader = new FileReader()
    reader.onloadend = () => {
      setPreviewImage(reader.result as string)
    }
    reader.readAsDataURL(file)

    // Загрузка на сервер
    setUploading(true)
    try {
      const uploadFormData = new FormData()
      uploadFormData.append('file', file)
      const response = await mediaApi.upload(uploadFormData)
      setFormData(prev => ({ ...prev, photo_id: response.image_id }))
      toast.success('Изображение загружено')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка загрузки изображения')
      setPreviewImage(null)
    } finally {
      setUploading(false)
    }
  }

  const handleRemoveImage = () => {
    setPreviewImage(null)
    setFormData(prev => ({ ...prev, photo_id: '' }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.photo_id) {
      toast.error('Загрузите изображение кафе')
      return
    }

    setLoading(true)
    try {
      await cafesApi.createCafe(formData)
      toast.success('Кафе создано успешно!')
      navigate('/cafes')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка создания кафе')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8 max-w-3xl mx-auto">
      <button
        onClick={() => navigate('/cafes')}
        className="text-primary-600 hover:text-primary-700 mb-6 inline-flex items-center"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Назад
      </button>

      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Создание кафе</h1>
        <p className="mt-2 text-gray-600">Заполните информацию о новом кафе</p>
      </div>

      <form onSubmit={handleSubmit} className="card space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Название кафе <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            required
            minLength={1}
            maxLength={200}
            className="input"
            placeholder="Название кафе"
            value={formData.name}
            onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Адрес <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            required
            minLength={1}
            className="input"
            placeholder="Адрес кафе"
            value={formData.address}
            onChange={(e) => setFormData(prev => ({ ...prev, address: e.target.value }))}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Телефон <span className="text-red-500">*</span>
          </label>
          <input
            type="tel"
            required
            minLength={1}
            className="input"
            placeholder="+79991234567"
            value={formData.phone}
            onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Описание
          </label>
          <textarea
            className="input"
            rows={4}
            placeholder="Описание кафе"
            value={formData.description}
            onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Users className="h-4 w-4 inline mr-2" />
            Менеджеры кафе
          </label>
          {loadingManagers ? (
            <p className="text-sm text-gray-500">Загрузка менеджеров...</p>
          ) : availableManagers.length === 0 ? (
            <p className="text-sm text-yellow-600">
              Нет доступных менеджеров. Сначала создайте пользователей с ролью "manager".
            </p>
          ) : (
            <div className="border border-gray-300 rounded-lg p-4 max-h-48 overflow-y-auto">
              {availableManagers.map((manager) => (
                <label
                  key={manager.id}
                  className="flex items-center space-x-2 py-2 cursor-pointer hover:bg-gray-50 rounded px-2"
                >
                  <input
                    type="checkbox"
                    checked={formData.managers_id?.includes(manager.id) || false}
                    onChange={() => toggleManager(manager.id)}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <div className="flex-1">
                    <span className="text-sm font-medium text-gray-900">{manager.username}</span>
                    <span className="text-xs text-gray-500 ml-2">({manager.email})</span>
                  </div>
                </label>
              ))}
            </div>
          )}
          {formData.managers_id && formData.managers_id.length > 0 && (
            <p className="mt-2 text-sm text-gray-600">
              Выбрано менеджеров: {formData.managers_id.length}
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Фото кафе <span className="text-red-500">*</span>
          </label>
          {!previewImage ? (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <label className="cursor-pointer">
                <span className="btn btn-secondary">
                  Выбрать изображение
                </span>
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleFileChange}
                  disabled={uploading}
                />
              </label>
              <p className="mt-2 text-sm text-gray-500">
                {uploading ? 'Загрузка...' : 'JPG, PNG или GIF'}
              </p>
            </div>
          ) : (
            <div className="relative">
              <img
                src={previewImage}
                alt="Preview"
                className="w-full h-64 object-cover rounded-lg"
              />
              <button
                type="button"
                onClick={handleRemoveImage}
                className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-2 hover:bg-red-600"
              >
                <X className="h-4 w-4" />
              </button>
              {formData.photo_id && (
                <p className="mt-2 text-sm text-green-600">✓ Изображение загружено</p>
              )}
            </div>
          )}
        </div>

        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate('/cafes')}
            className="btn btn-secondary"
            disabled={loading}
          >
            Отмена
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !formData.photo_id}
          >
            {loading ? 'Создание...' : 'Создать кафе'}
          </button>
        </div>
      </form>
    </div>
  )
}

