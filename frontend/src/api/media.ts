import apiClient from './client'

export interface MediaUploadResponse {
  image_id: string
}

export const mediaApi = {
  upload: async (formData: FormData): Promise<MediaUploadResponse> => {
    const response = await apiClient.post('/media/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
  
  getImage: (imageId: string): string => {
    return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/media/${imageId}`
  },
}

