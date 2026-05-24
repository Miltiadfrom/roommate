import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Добавляем токен к запросам
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Обработка ошибок авторизации
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('userId');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (phone, password) => 
    api.post('/auth/login', { phone, password }),
  
  register: (phone, password) => 
    api.post('/auth/register', { phone, password }),
};

export const profileAPI = {
  getMyProfile: () => api.get('/profile/me'),
  updateProfile: (data) => api.put('/profile/me', data),
  getProfile: (userId) => api.get(`/profile/${userId}`),
};

export const swipeAPI = {
  getCandidates: () => api.get('/candidates'),
  createSwipe: (targetUserId, direction) => 
    api.post('/swipe', { target_user_id: targetUserId, direction }),
};

export const matchAPI = {
  getMatches: () => api.get('/matches'),
};

export const messageAPI = {
  sendMessage: (receiverId, content) => 
    api.post(`/messages/${receiverId}`, { content }),
  getConversation: (otherUserId) => 
    api.get(`/messages/${otherUserId}`),
  getContacts: () => api.get('/contacts'),
};

export const compatibilityAPI = {
  getCompatibility: (candidateId) => 
    api.get(`/compatibility/${candidateId}`),
};

export default api;
