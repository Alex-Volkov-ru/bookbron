import apiClient from './client'

export interface User {
  id: number
  username: string
  email: string
  phone?: string
  role: string
  active: boolean
}

export interface UserShortInfo {
  id: number
  username: string
  email: string
  phone?: string
}

export const usersApi = {
  getUsers: async (): Promise<User[]> => {
    const response = await apiClient.get('/users')
    return response.data
  },
  
  getMe: async (): Promise<User> => {
    const response = await apiClient.get('/users/me')
    return response.data
  },
}

