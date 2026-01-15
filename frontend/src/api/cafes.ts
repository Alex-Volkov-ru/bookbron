import apiClient from './client'

export interface Cafe {
  id: number
  name: string
  address: string
  phone?: string
  description?: string
  photo?: string
  photo_id?: string
  active: boolean
  is_active?: boolean
  manager_ids?: number[]
  managers?: Array<{ id: number; username: string; email: string }>
  work_start_time?: string  // Формат: "HH:mm:ss" или "HH:mm"
  work_end_time?: string    // Формат: "HH:mm:ss" или "HH:mm"
  slot_duration_minutes?: number
  created_at: string
  updated_at: string
}

export interface CafeCreate {
  name: string
  address: string
  phone: string
  description?: string
  photo_id: string
  managers_id?: number[]
  work_start_time?: string  // Формат: "HH:mm" (например, "09:00")
  work_end_time?: string    // Формат: "HH:mm" (например, "22:00")
  slot_duration_minutes?: number  // 30, 40, 60 минут
}

export interface Table {
  id: number
  cafe_id: number
  seats_count: number
  description?: string
  active: boolean
}

export interface Slot {
  id: number
  cafe_id: number
  start_time: string
  end_time: string
  active: boolean
}

export const cafesApi = {
  getCafes: async (): Promise<Cafe[]> => {
    const response = await apiClient.get('/cafes?active_only=true')
    return response.data
  },
  
  getCafe: async (id: number): Promise<Cafe> => {
    const response = await apiClient.get(`/cafes/${id}`)
    return response.data
  },
  
  // Устаревшие методы - используйте tablesApi и slotsApi вместо них
  getTables: async (cafeId: number): Promise<Table[]> => {
    const response = await apiClient.get(`/cafe/${cafeId}/tables?active_only=true`)
    return response.data
  },
  
  getSlots: async (cafeId: number): Promise<Slot[]> => {
    const response = await apiClient.get(`/cafe/${cafeId}/slots?active_only=true`)
    return response.data
  },
  
  createCafe: async (data: CafeCreate): Promise<Cafe> => {
    const response = await apiClient.post('/cafes', data)
    return response.data
  },
}

