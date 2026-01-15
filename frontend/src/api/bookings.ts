import apiClient from './client'

export interface BookingDish {
  dish_id: number
  quantity: number
}

export interface Booking {
  id: number
  user_id: number
  cafe_id: number
  table_id: number
  slot_id: number
  date: string
  status: 'pending' | 'confirmed' | 'cancelled' | 'completed'
  note?: string
  reminder_sent: boolean
  active: boolean
  dishes: Array<{
    id: number
    dish_id: number
    dish_name: string
    quantity: number
    price: number
  }>
  created_at: string
  updated_at: string
}

export interface BookingCreate {
  cafe_id: number
  table_id: number
  slot_id: number
  date: string
  note?: string
  dishes?: BookingDish[]
}

export const bookingsApi = {
  getBookings: async (): Promise<Booking[]> => {
    const response = await apiClient.get('/booking')
    return response.data
  },
  
  getBooking: async (id: number): Promise<Booking> => {
    const response = await apiClient.get(`/booking/${id}`)
    return response.data
  },
  
  createBooking: async (data: BookingCreate): Promise<Booking> => {
    const response = await apiClient.post('/booking', data)
    return response.data
  },
  
  updateBooking: async (id: number, data: Partial<BookingCreate>): Promise<Booking> => {
    const response = await apiClient.put(`/booking/${id}`, data)
    return response.data
  },
  
  cancelBooking: async (id: number): Promise<void> => {
    await apiClient.delete(`/booking/${id}`)
  },
}

