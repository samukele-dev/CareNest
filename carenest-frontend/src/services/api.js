// api.js - UPDATED TO MATCH YOUR ACTUAL DJANGO ENDPOINTS
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000', 
  timeout: 10000,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  console.log("Token in interceptor:", token);
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    console.log("Authorization header set");
  } else {
    console.log("No token found in localStorage");
  }
  
  // Debug logging
  console.log(`API Request: ${config.method.toUpperCase()} ${config.baseURL}${config.url}`);
  console.log("Headers:", config.headers);
  
  // Mandatory trailing slash for Django
  if (!config.url.endsWith('/') && !config.url.includes('?')) {
    config.url += '/';
  }
  return config;
});

// SINGLE Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log("API Response:", response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error("API Error:", error.response?.status, error.config?.url);
    if (error.response?.status === 401) {
      console.log("Unauthorized, clearing tokens");
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// CAREGIVER API
export const caregiverAPI = {
  // Get current caregiver profile
  getMyProfile: async () => {
    const response = await api.get('/api/profiles/caregiver/me/');
    return response.data;
  },

  // Update current caregiver profile
  updateMyProfile: async (profileData) => {
    const response = await api.patch('/api/profiles/caregiver/me/', profileData);
    return response.data;
  },

  // Create caregiver profile
  createProfile: async (profileData) => {
    const response = await api.post('/api/profiles/caregiver/me/', profileData);
    return response.data;
  },

  // Get dashboard stats
  getDashboardStats: async () => {
    const response = await api.get('/api/profiles/caregiver/dashboard_stats/');
    return response.data;
  },

  // Update availability
  updateAvailability: async (availabilityData) => {
    const response = await api.patch('/api/profiles/caregiver/update_availability/', availabilityData);
    return response.data;
  },

  // Complete profile wizard
  completeProfile: async (profileData) => {
    const response = await api.post('/api/profiles/caregiver/complete_profile/', profileData);
    return response.data;
  },
};


// APPOINTMENTS API
export const appointmentsAPI = {
  // Get all appointments for current user
  getAppointments: async () => {
    const response = await api.get('/api/profiles/appointments/');
    return response.data;
  },

  // Get upcoming appointments
  getUpcomingAppointments: async () => {
    const response = await api.get('/api/profiles/appointments/upcoming/');
    return response.data;
  },

  // Get appointment by ID
  getAppointment: async (id) => {
    const response = await api.get(`/api/profiles/appointments/${id}/`);
    return response.data;
  },

  // Create new appointment
  createAppointment: async (appointmentData) => {
    const response = await api.post('/api/profiles/appointments/', appointmentData);
    return response.data;
  },

  // Update appointment
  updateAppointment: async (id, appointmentData) => {
    const response = await api.patch(`/api/profiles/appointments/${id}/`, appointmentData);
    return response.data;
  },

  // Confirm appointment
  confirmAppointment: async (id) => {
    const response = await api.post(`/api/profiles/appointments/${id}/confirm/`);
    return response.data;
  },

  // Complete appointment
  completeAppointment: async (id) => {
    const response = await api.post(`/api/profiles/appointments/${id}/complete/`);
    return response.data;
  },
};

// AUTH API
export const authAPI = {
  login: async (credentials) => {
    const response = await api.post('/api/auth/login/', credentials);
    
    if (response.data.key) {
      localStorage.setItem('access_token', response.data.key);
    } else if (response.data.access) {
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
    }
    
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/api/auth/registration/', userData);
    if (response.data.key) {
      localStorage.setItem('access_token', response.data.key);
    }
    return response.data;
  },

  logout: async () => {
    try {
      await api.post('/api/auth/logout/');
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/auth/user/');
    return response.data;
  },
};

// SEARCH API
export const searchAPI = {
  // Search caregivers
  searchCaregivers: async (filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value);
      }
    });
    const url = `/api/profiles/caregiver/discovery/?${params.toString()}`;
    const response = await api.get(url);
    return response.data;
  },
};

// AVAILABILITY API
export const availabilityAPI = {
  getAvailability: async () => {
    const response = await api.get('/api/profiles/availability/');
    return response.data;
  },

  createAvailability: async (availabilityData) => {
    const response = await api.post('/api/profiles/availability/', availabilityData);
    return response.data;
  },

  updateAvailability: async (id, availabilityData) => {
    const response = await api.patch(`/api/profiles/availability/${id}/`, availabilityData);
    return response.data;
  },

  deleteAvailability: async (id) => {
    const response = await api.delete(`/api/profiles/availability/${id}/`);
    return response.data;
  },
};

// NOTIFICATIONS API
export const notificationsAPI = {
  getNotifications: async () => {
    const response = await api.get('/api/profiles/notifications/');
    return response.data;
  },

  markAsRead: async (id) => {
    const response = await api.patch(`/api/profiles/notifications/${id}/`, { is_read: true });
    return response.data;
  },

  markAllAsRead: async () => {
    const response = await api.post('/api/profiles/notifications/mark_all_read/');
    return response.data;
  },
};

export default api;