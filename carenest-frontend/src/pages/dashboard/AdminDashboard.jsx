import React from 'react';
import { Container, Typography, Box, Button } from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';
import Navbar from '../../components/layout/Navbar';
import { colors } from '../../components/ui/styled';

const AdminDashboard = () => {
  const { user, logout } = useAuth();

  return (
    <>
      <Navbar />
      <Container maxWidth="lg" sx={{ py: 4, mt: 8 }}>
        <Typography variant="h4" sx={{ color: colors.taupe, mb: 3 }}>
          Welcome, Admin {user?.firstName || 'Administrator'}!
        </Typography>
        <Box sx={{ bgcolor: 'white', p: 4, borderRadius: 3, boxShadow: 2 }}>
          <Typography sx={{ color: colors.brown }}>
            This is the Admin Dashboard. Features will be added here.
          </Typography>
          <Button 
            onClick={logout}
            sx={{ mt: 3, color: colors.sage }}
          >
            Logout
          </Button>
        </Box>
      </Container>
    </>
  );
};

export default AdminDashboard;