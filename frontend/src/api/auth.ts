import apiClient from './client'

export interface LoginCredentials {
  login: string  // email or phone
  password: string
}

export interface User {
  id: number
  username: string
  email: string
  phone?: string
  role: string
  active: boolean
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface RegisterData {
  username: string
  email?: string
  phone?: string
  password: string
}

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await apiClient.post('/auth/login', credentials)
    return response.data
  },
  
  register: async (data: RegisterData): Promise<User> => {
    const response = await apiClient.post('/users', data)
    return response.data
  },
  
  getMe: async (): Promise<User> => {
    const response = await apiClient.get('/users/me')
    return response.data
  },
}

