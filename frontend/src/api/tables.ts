import apiClient from './client'

export interface Table {
  id: number
  cafe_id: number
  seats_count: number
  description?: string
  active: boolean
  created_at: string
  updated_at: string
}

export interface TableCreate {
  seats_count: number
  description?: string
}

export interface TableUpdate {
  cafe_id?: number
  seats_count?: number
  description?: string
  active?: boolean
}

export const tablesApi = {
  getTables: async (cafeId: number, bookingDate?: string, slotId?: number, activeOnly: boolean = false): Promise<Table[]> => {
    let url = `/cafe/${cafeId}/tables?active_only=${activeOnly}`
    if (bookingDate) url += `&booking_date=${bookingDate}`
    if (slotId) url += `&slot_id=${slotId}`
    const response = await apiClient.get(url)
    return response.data
  },
  
  getTable: async (cafeId: number, tableId: number): Promise<Table> => {
    const response = await apiClient.get(`/cafe/${cafeId}/tables/${tableId}`)
    return response.data
  },
  
  createTable: async (cafeId: number, data: TableCreate): Promise<Table> => {
    const response = await apiClient.post(`/cafe/${cafeId}/tables`, data)
    return response.data
  },
  
  updateTable: async (cafeId: number, tableId: number, data: TableUpdate): Promise<Table> => {
    const response = await apiClient.patch(`/cafe/${cafeId}/tables/${tableId}`, data)
    return response.data
  },
  
  deleteTable: async (cafeId: number, tableId: number): Promise<void> => {
    await apiClient.delete(`/cafe/${cafeId}/tables/${tableId}`)
  },
}

