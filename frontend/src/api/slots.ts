import apiClient from './client'

export interface Slot {
  id: number
  cafe_id: number
  start_time: string
  end_time: string
  active: boolean
  created_at: string
  updated_at: string
}

export interface SlotCreate {
  start_time: string
  end_time: string
}

export interface SlotUpdate {
  cafe_id?: number
  start_time?: string
  end_time?: string
  active?: boolean
}

export const slotsApi = {
  getSlots: async (cafeId: number, bookingDate?: string, tableId?: number, activeOnly: boolean = false): Promise<Slot[]> => {
    let url = `/cafe/${cafeId}/slots?active_only=${activeOnly}`
    if (bookingDate) url += `&booking_date=${bookingDate}`
    if (tableId) url += `&table_id=${tableId}`
    const response = await apiClient.get(url)
    return response.data
  },
  
  getSlot: async (cafeId: number, slotId: number): Promise<Slot> => {
    const response = await apiClient.get(`/cafe/${cafeId}/slots/${slotId}`)
    return response.data
  },
  
  createSlot: async (cafeId: number, data: SlotCreate): Promise<Slot> => {
    const response = await apiClient.post(`/cafe/${cafeId}/slots`, data)
    return response.data
  },
  
  updateSlot: async (cafeId: number, slotId: number, data: SlotUpdate): Promise<Slot> => {
    const response = await apiClient.patch(`/cafe/${cafeId}/slots/${slotId}`, data)
    return response.data
  },
  
  deleteSlot: async (cafeId: number, slotId: number): Promise<void> => {
    await apiClient.delete(`/cafe/${cafeId}/slots/${slotId}`)
  },
  
  generateSlots: async (cafeId: number): Promise<Slot[]> => {
    const response = await apiClient.post(`/cafe/${cafeId}/slots/generate`)
    return response.data
  },
}

