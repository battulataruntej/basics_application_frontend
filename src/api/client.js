import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  signup: async (email, username, password) => {
    const response = await apiClient.post('/signup', { email, username, password });
    return response.data;
  },
  
  login: async (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await apiClient.post('/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },
  
  getMe: async () => {
    const response = await apiClient.get('/me');
    return response.data;
  },
};

// Course API
export const courseAPI = {
  getCourses: async () => {
    const response = await apiClient.get('/courses');
    return response.data;
  },
  
  getCourse: async (courseId) => {
    const response = await apiClient.get(`/courses/${courseId}`);
    return response.data;
  },
};

// Session API
export const sessionAPI = {
  createSession: async (environmentType = 'ubuntu') => {
    const response = await apiClient.post('/sessions/create', null, {
      params: { environment_type: environmentType },
    });
    return response.data;
  },
  
  getSessions: async () => {
    const response = await apiClient.get('/sessions');
    return response.data;
  },
  
  deleteSession: async (sessionId) => {
    const response = await apiClient.delete(`/sessions/${sessionId}`);
    return response.data;
  },
};

export default apiClient;