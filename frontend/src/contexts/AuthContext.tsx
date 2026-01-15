import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authApi, User, RegisterData } from '../api/auth'
import toast from 'react-hot-toast'

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser))
        // Проверяем токен
        authApi.getMe()
          .then((userData) => {
            setUser(userData)
            localStorage.setItem('user', JSON.stringify(userData))
          })
          .catch(() => {
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            setUser(null)
          })
          .finally(() => setLoading(false))
      } catch {
        setLoading(false)
      }
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const response = await authApi.login({ login: email, password })
      localStorage.setItem('token', response.access_token)
      
      const userData = await authApi.getMe()
      setUser(userData)
      localStorage.setItem('user', JSON.stringify(userData))
      
      toast.success('Вход выполнен успешно!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка входа')
      throw error
    }
  }

  const register = async (data: RegisterData) => {
    try {
      await authApi.register(data)
      toast.success('Регистрация выполнена успешно! Теперь вы можете войти.')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка регистрации')
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
    toast.success('Выход выполнен')
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

