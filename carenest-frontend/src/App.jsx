import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Navbar from './components/layout/Navbar';

// Lazy load pages for better performance
const Landing = lazy(() => import('./pages/Landing'));
const Login = lazy(() => import('./pages/auth/Login'));
const Register = lazy(() => import('./pages/auth/Register'));
const ClientDashboard = lazy(() => import('./pages/dashboard/ClientDashboard'));
const CaregiverDashboard = lazy(() => import('./pages/dashboard/CaregiverDashboard'));
const AdminDashboard = lazy(() => import('./pages/dashboard/AdminDashboard'));

// Loading component
const Loader = () => (
  <Box
    sx={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      bgcolor: '#F9F3E5',
    }}
  >
    <CircularProgress sx={{ color: '#8B9474' }} />
  </Box>
);

// Protected Route component
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    return <Loader />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  if (allowedRoles && !allowedRoles.includes(user?.type)) {
    return <Navigate to="/" />;
  }

  return children;
};

// Public Route component (redirects if logged in)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    return <Loader />;
  }

  if (isAuthenticated) {
    // Redirect to appropriate dashboard
    switch (user?.type) {
      case 'client':
        return <Navigate to="/dashboard/client" />;
      case 'caregiver':
        return <Navigate to="/dashboard/caregiver" />;
      case 'admin':
        return <Navigate to="/dashboard/admin" />;
      default:
        return <Navigate to="/" />;
    }
  }

  return children;
};

function AppContent() {
  return (
    <Suspense fallback={<Loader />}>
      <Routes>
        {/* Public Routes */}
        <Route
          path="/"
          element={
            <>
              <Navbar />
              <Landing />
            </>
          }
        />
        
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        
        <Route
          path="/register"
          element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          }
        />

        {/* Protected Dashboard Routes */}
        <Route
          path="/dashboard/client"
          element={
            <ProtectedRoute allowedRoles={['client', 'admin']}>
              <ClientDashboard />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/dashboard/caregiver"
          element={
            <ProtectedRoute allowedRoles={['caregiver', 'admin']}>
              <CaregiverDashboard />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/dashboard/admin"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />

        {/* 404 Route */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Suspense>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;