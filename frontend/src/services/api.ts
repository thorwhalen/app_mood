import axios from 'axios';
import type {
  Mood,
  MoodCreate,
  Dataset,
  DatasetCreate,
  DatasetExample,
  MLModel,
  Analysis,
  AnalysisCreate,
  HeadlineAnalysis,
  Task,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Moods API
export const moodsApi = {
  list: () => api.get<Mood[]>('/moods'),
  get: (id: string) => api.get<Mood>(`/moods/${id}`),
  create: (data: MoodCreate) => api.post<Mood>('/moods', data),
  update: (id: string, data: Partial<MoodCreate>) => api.put<Mood>(`/moods/${id}`, data),
  delete: (id: string) => api.delete(`/moods/${id}`),
};

// Datasets API
export const datasetsApi = {
  generate: (moodId: string, data: DatasetCreate) =>
    api.post<Dataset>(`/datasets/${moodId}/generate`, data),
  get: (id: string) => api.get<Dataset>(`/datasets/${id}`),
  getExamples: (id: string, skip = 0, limit = 100) =>
    api.get<DatasetExample[]>(`/datasets/${id}/examples`, {
      params: { skip, limit },
    }),
  listByMood: (moodId: string) => api.get<Dataset[]>(`/datasets/mood/${moodId}`),
};

// Models API
export const modelsApi = {
  train: (moodId: string, datasetId: string) =>
    api.post(`/models/${moodId}/train`, { dataset_id: datasetId }),
  get: (id: string) => api.get<MLModel>(`/models/${id}`),
  listByMood: (moodId: string) => api.get<MLModel[]>(`/models/mood/${moodId}`),
  select: (id: string) => api.post<MLModel>(`/models/${id}/select`),
};

// Analysis API
export const analysisApi = {
  analyze: (data: AnalysisCreate) => api.post<Analysis>('/analysis', data),
  analyzeBatch: (moodId: string, texts: string[]) =>
    api.post('/analysis/batch', { mood_id: moodId, texts }),
  list: (moodId?: string, skip = 0, limit = 100) =>
    api.get<Analysis[]>('/analysis', {
      params: { mood_id: moodId, skip, limit },
    }),
  headlines: () => api.get<HeadlineAnalysis[]>('/analysis/headlines'),
  exportCsv: (moodId?: string) =>
    api.get('/analysis/export/csv', {
      params: { mood_id: moodId },
      responseType: 'blob',
    }),
};

// Tasks API
export const tasksApi = {
  get: (id: string) => api.get<Task>(`/tasks/${id}`),
};

// Admin API
export const adminApi = {
  getStats: () => api.get<any>('/admin/stats'),
  getUsers: (skip = 0, limit = 100) =>
    api.get<any[]>('/admin/users', { params: { skip, limit } }),
  updateUserQuota: (userId: string, quotaData: any) =>
    api.patch(`/admin/users/${userId}/quota`, quotaData),
  toggleUserActive: (userId: string, active: boolean) =>
    api.patch(`/admin/users/${userId}/activate`, null, { params: { active } }),
  getAnalysesOverTime: (days = 30) =>
    api.get<any>('/admin/analytics/analyses-over-time', { params: { days } }),
  getUserGrowth: (days = 30) =>
    api.get<any>('/admin/analytics/user-growth', { params: { days } }),
  getTopMoods: (limit = 10) =>
    api.get<any>('/admin/analytics/top-moods', { params: { limit } }),
};

// Auth/User API
export const authApi = {
  getUsage: () => api.get<any>('/auth/usage'),
  getCurrentUser: () => api.get<any>('/auth/me'),
};

export default api;
