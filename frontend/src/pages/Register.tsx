import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Coffee } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Register() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (password !== confirmPassword) {
      toast.error('Пароли не совпадают')
      return
    }

    if (!email && !phone) {
      toast.error('Укажите email или телефон')
      return
    }

    setLoading(true)

    try {
      await register({ username, email: email || undefined, phone: phone || undefined, password })
      navigate('/login')
    } catch (error) {
      // Ошибка уже обработана в AuthContext
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="flex justify-center">
            <Coffee className="h-16 w-16 text-primary-600" />
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Регистрация
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Создайте аккаунт для бронирования мест в кафе
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm space-y-4">
            <div>
              <label htmlFor="username" className="sr-only">
                Имя пользователя
              </label>
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                required
                minLength={3}
                className="input rounded-md"
                placeholder="Имя пользователя"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="email" className="sr-only">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                className="input rounded-md"
                placeholder="Email адрес (или телефон)"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="phone" className="sr-only">
                Телефон
              </label>
              <input
                id="phone"
                name="phone"
                type="tel"
                autoComplete="tel"
                className="input rounded-md"
                placeholder="Телефон (или email)"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Пароль
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                minLength={6}
                className="input rounded-md"
                placeholder="Пароль (минимум 6 символов)"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="confirmPassword" className="sr-only">
                Подтверждение пароля
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                required
                className="input rounded-md"
                placeholder="Подтвердите пароль"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>
            {password && confirmPassword && password !== confirmPassword && (
              <p className="text-sm text-red-600">Пароли не совпадают</p>
            )}
            {!email && !phone && (email !== '' || phone !== '') && (
              <p className="text-sm text-red-600">Укажите email или телефон</p>
            )}
          </div>

          <div>
            <button
              type="submit"
              disabled={loading || password !== confirmPassword || (!email && !phone)}
              className="btn btn-primary w-full py-3 text-base"
            >
              {loading ? 'Регистрация...' : 'Зарегистрироваться'}
            </button>
          </div>

          <div className="text-center text-sm text-gray-600">
            <p>
              Уже есть аккаунт?{' '}
              <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">
                Войти
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  )
}

