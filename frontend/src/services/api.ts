import axios from 'axios'
import { User, Workspace, FileItem, JupyterStatus } from '../types'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
})

// 토큰 인터셉터
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 인증 API
export const authAPI = {
  login: async (username: string, password: string) => {
    const response = await api.post('/auth/login', {
      email: username,
      password: password,
    })
    return response.data
  },

  register: async (username: string, email: string, password: string) => {
    const response = await api.post('/auth/register', {
      username,
      email,
      password,
    })
    return response.data
  },

  getMe: async (): Promise<User> => {
    const response = await api.get('/auth/me')
    return response.data
  },
}

// 워크스페이스 API
export const workspaceAPI = {
  list: async (): Promise<Workspace[]> => {
    const response = await api.get('/workspaces/')
    return response.data
  },

  create: async (name: string, description?: string): Promise<Workspace> => {
    const response = await api.post('/workspaces/', {
      name,
      description,
    })
    return response.data
  },

  get: async (id: number): Promise<Workspace> => {
    const response = await api.get(`/workspaces/${id}`)
    return response.data
  },

  delete: async (id: number) => {
    const response = await api.delete(`/workspaces/${id}`)
    return response.data
  },
}

// Jupyter API
export const jupyterAPI = {
  start: async (workspaceId: number) => {
    const response = await api.post(`/jupyter/start/${workspaceId}`)
    return response.data
  },

  stop: async (workspaceId: number) => {
    const response = await api.post(`/jupyter/stop/${workspaceId}`)
    return response.data
  },

  getStatus: async (workspaceId: number): Promise<JupyterStatus> => {
    const response = await api.get(`/jupyter/status/${workspaceId}`)
    return response.data
  },
}

// 파일 API
export const fileAPI = {
  list: async (workspaceId: number, path: string = ''): Promise<{ files: FileItem[], current_path: string }> => {
    const response = await api.get(`/files/${workspaceId}/list`, {
      params: { path },
    })
    return response.data
  },

  upload: async (workspaceId: number, files: FileList, path: string = '') => {
    const formData = new FormData()
    Array.from(files).forEach((file) => {
      formData.append('files', file)
    })
    
    const response = await api.post(`/files/${workspaceId}/upload`, formData, {
      params: { path },
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  download: async (workspaceId: number, filePath: string) => {
    const response = await api.get(`/files/${workspaceId}/download`, {
      params: { file_path: filePath },
      responseType: 'blob',
    })
    return response.data
  },

  delete: async (workspaceId: number, filePath: string) => {
    const response = await api.delete(`/files/${workspaceId}/delete`, {
      params: { file_path: filePath },
    })
    return response.data
  },

  createFolder: async (workspaceId: number, folderName: string, path: string = '') => {
    const response = await api.post(`/files/${workspaceId}/create-folder`, null, {
      params: { folder_name: folderName, path },
    })
    return response.data
  },
}

export default api 