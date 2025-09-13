import axios from 'axios';
import {
  Route,
  Train,
  Schedule,
  OptimizationTask,
  PerformanceMetric,
  DashboardMetrics,
  ApiResponse,
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const routeApi = {
  getAll: (params?: Record<string, any>) =>
    api.get<ApiResponse<Route>>('/routes/', { params }),
  get: (id: number) => api.get<Route>(`/routes/${id}/`),
  create: (data: Partial<Route>) => api.post<Route>('/routes/', data),
  update: (id: number, data: Partial<Route>) =>
    api.put<Route>(`/routes/${id}/`, data),
  delete: (id: number) => api.delete(`/routes/${id}/`),
  getPerformance: (id: number, days = 30) =>
    api.get(`/routes/${id}/performance/`, { params: { days } }),
  getActive: () => api.get<Route[]>('/routes/active/'),
};

export const trainApi = {
  getAll: (params?: Record<string, any>) =>
    api.get<ApiResponse<Train>>('/trains/', { params }),
  get: (id: number) => api.get<Train>(`/trains/${id}/`),
  create: (data: Partial<Train>) => api.post<Train>('/trains/', data),
  update: (id: number, data: Partial<Train>) =>
    api.put<Train>(`/trains/${id}/`, data),
  delete: (id: number) => api.delete(`/trains/${id}/`),
  getOperational: () => api.get<Train[]>('/trains/operational/'),
  getSchedules: (id: number, params?: Record<string, any>) =>
    api.get<Schedule[]>(`/trains/${id}/schedules/`, { params }),
};

export const scheduleApi = {
  getAll: (params?: Record<string, any>) =>
    api.get<ApiResponse<Schedule>>('/schedules/', { params }),
  get: (id: number) => api.get<Schedule>(`/schedules/${id}/`),
  create: (data: Partial<Schedule>) => api.post<Schedule>('/schedules/', data),
  update: (id: number, data: Partial<Schedule>) =>
    api.put<Schedule>(`/schedules/${id}/`, data),
  delete: (id: number) => api.delete(`/schedules/${id}/`),
  getToday: () => api.get<Schedule[]>('/schedules/today/'),
  getUpcoming: () => api.get<Schedule[]>('/schedules/upcoming/'),
};

export const optimizationApi = {
  getAll: (params?: Record<string, any>) =>
    api.get<ApiResponse<OptimizationTask>>('/optimization-tasks/', { params }),
  get: (id: number) => api.get<OptimizationTask>(`/optimization-tasks/${id}/`),
  create: (data: { optimization_type: string; parameters: Record<string, any> }) =>
    api.post<OptimizationTask>('/optimization-tasks/', data),
  restart: (id: number) =>
    api.post(`/optimization-tasks/${id}/restart/`),
  getMyTasks: () => api.get<OptimizationTask[]>('/optimization-tasks/my_tasks/'),
};

export const performanceApi = {
  getAll: (params?: Record<string, any>) =>
    api.get<ApiResponse<PerformanceMetric>>('/performance-metrics/', { params }),
  get: (id: number) => api.get<PerformanceMetric>(`/performance-metrics/${id}/`),
  create: (data: Partial<PerformanceMetric>) =>
    api.post<PerformanceMetric>('/performance-metrics/', data),
  getDashboard: () =>
    api.get<DashboardMetrics>('/performance-metrics/dashboard/'),
  getTrends: (type: string, days = 30) =>
    api.get('/performance-metrics/trends/', { params: { type, days } }),
  getSummary: () => api.get('/performance-metrics/summary/'),
};

export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login/', { username, password }),
  logout: () => api.post('/auth/logout/'),
  getCurrentUser: () => api.get('/auth/user/'),
};

export default api;