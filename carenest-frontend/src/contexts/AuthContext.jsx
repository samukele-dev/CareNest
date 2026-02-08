import { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';

const AuthContext = createContext({});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        const userData = await authAPI.getCurrentUser();
        setUser({
          ...userData,
          type: userData.user_type || 'client',
        });
      }
    } catch (err) {
      console.error('Auth check failed:', err);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setError(null);
      const data = await authAPI.login({ email, password });
      
      // Store tokens
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      
      // Get user data
      const userData = await authAPI.getCurrentUser();
      const authenticatedUser = {
        ...userData,
        type: userData.user_type || 'client',
      };
      
      setUser(authenticatedUser);
      
      // Redirect based on user type
      switch (authenticatedUser.type) {
        case 'client':
          navigate('/dashboard/client');
          break;
        case 'caregiver':
          navigate('/dashboard/caregiver');
          break;
        case 'admin':
          navigate('/dashboard/admin');
          break;
        default:
          navigate('/dashboard');
      }
      
      return { success: true };
    } catch (err) {
      setError(err.response?.data || 'Login failed');
      return { success: false, error: err.response?.data };
    }
  };

  const register = async (userData) => {
    try {
      setError(null);
      
      // Format data for Django REST Auth registration
      const registrationData = {
        email: userData.email,
        password1: userData.password,
        password2: userData.confirmPassword,
        first_name: userData.firstName,
        last_name: userData.lastName,
        user_type: userData.userType,
      };
      
      const data = await authAPI.register(registrationData);
      
      // Auto login after registration
      const loginData = await authAPI.login({
        email: userData.email,
        password: userData.password,
      });
      
      localStorage.setItem('access_token', loginData.access);
      localStorage.setItem('refresh_token', loginData.refresh);
      
      const userDataResponse = await authAPI.getCurrentUser();
      const authenticatedUser = {
        ...userDataResponse,
        type: userData.userType,
      };
      
      setUser(authenticatedUser);
      navigate(`/dashboard/${userData.userType}`);
      
      return { success: true };
    } catch (err) {
      setError(err.response?.data || 'Registration failed');
      return { success: false, error: err.response?.data };
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
      navigate('/');
    }
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};