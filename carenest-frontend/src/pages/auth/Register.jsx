/**
 * CareNest Pro - Premium Registration System
 * Version: 2.6.0 - Profile-Linked Registration with Privacy Policy Fix
 * * This component handles user creation and ensures all required fields 
 * are correctly sent to the Django backend.
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Container,
  Paper,
  Typography,
  Box,
  TextField,
  Button,
  Divider,
  IconButton,
  InputAdornment,
  Alert,
  FormControlLabel,
  Checkbox,
  Stack,
  Tooltip,
  CircularProgress,
  Fade
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Person,
  Email,
  Lock,
  ArrowForward,
  CheckCircleOutline,
  InfoOutlined,
  ShieldOutlined
} from '@mui/icons-material';
import styled from 'styled-components';
import { useAuth } from '../../contexts/AuthContext';
import { colors } from '../../components/ui/styled';

// =============================================================================
// STYLED COMPONENTS (High-Fidelity UI)
// =============================================================================

const RegisterContainer = styled(Box)`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at top right, ${colors.cream} 0%, #fdf5f0 100%);
  padding: 40px 20px;
`;

const RegisterPaper = styled(motion(Paper))`
  padding: 48px;
  border-radius: 32px;
  width: 100%;
  max-width: 550px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 116, 91, 0.1);
  box-shadow: 0 40px 100px rgba(93, 74, 62, 0.08);
`;

const BrandIcon = styled.div`
  width: 72px;
  height: 72px;
  background: linear-gradient(135deg, ${colors.sage} 0%, #738a80 100%);
  border-radius: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  color: white;
  font-weight: 900;
  font-size: 28px;
  box-shadow: 0 12px 24px rgba(141, 163, 153, 0.3);
`;

const TypeCard = styled(Box)`
  padding: 20px;
  border: 2px solid ${({ selected, color }) => selected ? color : 'rgba(139, 116, 91, 0.1)'};
  border-radius: 18px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  background: ${({ selected, color }) => selected ? `${color}08` : 'white'};
  text-align: center;
  flex: 1;
  
  &:hover {
    border-color: ${({ color }) => color};
    transform: translateY(-4px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.04);
  }
`;

const StyledInput = styled(TextField)`
  && {
    .MuiOutlinedInput-root {
      border-radius: 16px;
      background: white;
      transition: all 0.3s ease;
      
      &:hover .MuiOutlinedInput-notchedOutline {
        border-color: ${colors.sage};
      }
      
      &.Mui-focused .MuiOutlinedInput-notchedOutline {
        border-color: ${colors.sage};
        border-width: 2px;
      }
    }
  }
`;

// =============================================================================
// MAIN COMPONENT
// =============================================================================

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password1: '',
    password2: '',
    first_name: '',
    last_name: '',
    user_type: 'client',  // Default value as string, not null
    phone_number: '',  // Added this field (optional)
    terms_accepted: false,
    privacy_policy_accepted: false,  // Added this required field
    marketing_opt_in: false  // Added this optional field
  });

  const [uiState, setUiState] = useState({
    isLoading: false,
    error: null,
    showPass: false,
    showConfirm: false
  });

  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setUiState(prev => ({ ...prev, error: null, isLoading: true }));

    // Enhanced Validation
    if (!formData.terms_accepted || !formData.privacy_policy_accepted) {
      setUiState(prev => ({ 
        ...prev, 
        error: 'You must accept both Terms of Service and Privacy Policy to register.', 
        isLoading: false 
      }));
      return;
    }

    if (formData.password1 !== formData.password2) {
      setUiState(prev => ({ ...prev, error: 'Passwords do not match', isLoading: false }));
      return;
    }

    if (formData.password1.length < 8) {
      setUiState(prev => ({ ...prev, error: 'Password must be at least 8 characters', isLoading: false }));
      return;
    }

    // Prepare payload according to backend requirements
    const payload = {
      email: formData.email,
      password1: formData.password1,
      password2: formData.password2,
      first_name: formData.first_name,
      last_name: formData.last_name,
      user_type: formData.user_type, // This should be 'client' or 'caregiver' as string
      phone_number: formData.phone_number,
      terms_accepted: formData.terms_accepted,
      privacy_policy_accepted: formData.privacy_policy_accepted,
      marketing_opt_in: formData.marketing_opt_in
    };

    console.log('Sending registration payload:', payload); // Debug log

    try {
      const response = await fetch('http://127.0.0.1:8000/api/auth/registration/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      console.log('Registration response:', data); // Debug log

      if (response.ok) {
        // SUCCESS: Redirect to login or auto-login
        navigate('/login', { 
          state: { 
            message: 'Registration successful! Please sign in.',
            email: formData.email 
          } 
        });
      } else {
        // Parse Django REST Framework Errors
        let errorMessage = "Registration failed.";
        
        if (data && typeof data === 'object') {
          // Handle field-specific errors
          const errors = [];
          for (const [field, messages] of Object.entries(data)) {
            if (Array.isArray(messages)) {
              errors.push(...messages);
            } else if (typeof messages === 'string') {
              errors.push(messages);
            }
          }
          errorMessage = errors.length > 0 ? errors.join(' ') : errorMessage;
        }
        
        setUiState(prev => ({ 
          ...prev, 
          error: errorMessage, 
          isLoading: false 
        }));
      }
    } catch (err) {
      console.error('Registration error:', err);
      setUiState(prev => ({ 
        ...prev, 
        error: 'Connection to CareNest server failed. Please try again.', 
        isLoading: false 
      }));
    }
  };

  return (
    <RegisterContainer>
      <RegisterPaper
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <Box sx={{ textAlign: 'center', mb: 5 }}>
          <BrandIcon>CN</BrandIcon>
          <Typography variant="h3" sx={{ color: colors.brown, fontWeight: 900, letterSpacing: '-1px', mb: 1 }}>
            Create Account
          </Typography>
          <Typography variant="body1" sx={{ color: colors.taupe, opacity: 0.8 }}>
            Enter your details to join the CareNest community.
          </Typography>
        </Box>

        <AnimatePresence>
          {uiState.error && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}>
              <Alert 
                severity="error" 
                variant="filled" 
                sx={{ 
                  mb: 4, 
                  borderRadius: '16px', 
                  bgcolor: '#c62828',
                  '& .MuiAlert-icon': { fontSize: '24px' }
                }}
                onClose={() => setUiState(prev => ({ ...prev, error: null }))}
              >
                <Typography variant="body1" fontWeight={600}>{uiState.error}</Typography>
              </Alert>
            </motion.div>
          )}
        </AnimatePresence>

        <form onSubmit={handleRegister}>
          <Stack spacing={3}>
            {/* User Type Selection */}
            <Box>
              <Typography variant="subtitle2" sx={{ color: colors.taupe, mb: 2, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px' }}>
                I am registering as a:
              </Typography>
              <Stack direction="row" spacing={2}>
                {[
                  { id: 'client', label: 'Client', color: colors.sage, icon: '🏠' },
                  { id: 'caregiver', label: 'Caregiver', color: colors.peach, icon: '🩺' }
                ].map((type) => (
                  <TypeCard
                    key={type.id}
                    selected={formData.user_type === type.id}
                    color={type.color}
                    onClick={() => setFormData({ ...formData, user_type: type.id })}
                  >
                    <Typography variant="h4" sx={{ mb: 1 }}>{type.icon}</Typography>
                    <Typography variant="body2" fontWeight={700}>{type.label}</Typography>
                  </TypeCard>
                ))}
              </Stack>
            </Box>

            <Divider sx={{ my: 1, opacity: 0.5 }}>Account Information</Divider>

            <Stack direction="row" spacing={2}>
              <StyledInput
                label="First Name *"
                name="first_name"
                fullWidth
                required
                value={formData.first_name}
                onChange={handleChange}
                error={!formData.first_name.trim()}
                helperText={!formData.first_name.trim() ? "First name is required" : ""}
              />
              <StyledInput
                label="Last Name *"
                name="last_name"
                fullWidth
                required
                value={formData.last_name}
                onChange={handleChange}
                error={!formData.last_name.trim()}
                helperText={!formData.last_name.trim() ? "Last name is required" : ""}
              />
            </Stack>

            <StyledInput
              label="Email Address *"
              name="email"
              type="email"
              fullWidth
              required
              value={formData.email}
              onChange={handleChange}
              error={formData.email && !/\S+@\S+\.\S+/.test(formData.email)}
              helperText={formData.email && !/\S+@\S+\.\S+/.test(formData.email) ? "Enter a valid email address" : ""}
              InputProps={{
                startAdornment: <InputAdornment position="start"><Email sx={{ color: colors.sage }} /></InputAdornment>,
              }}
            />

            <StyledInput
              label="Phone Number (Optional)"
              name="phone_number"
              type="tel"
              fullWidth
              value={formData.phone_number}
              onChange={handleChange}
              placeholder="+1 234 567 8900"
              InputProps={{
                startAdornment: <InputAdornment position="start">📱</InputAdornment>,
              }}
            />

            <StyledInput
              label="Password *"
              name="password1"
              type={uiState.showPass ? 'text' : 'password'}
              fullWidth
              required
              value={formData.password1}
              onChange={handleChange}
              helperText="At least 8 characters"
              InputProps={{
                startAdornment: <InputAdornment position="start"><Lock sx={{ color: colors.sage }} /></InputAdornment>,
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setUiState({ ...uiState, showPass: !uiState.showPass })} edge="end">
                      {uiState.showPass ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <StyledInput
              label="Confirm Password *"
              name="password2"
              type={uiState.showConfirm ? 'text' : 'password'}
              fullWidth
              required
              value={formData.password2}
              onChange={handleChange}
              error={formData.password2 && formData.password1 !== formData.password2}
              helperText={formData.password2 && formData.password1 !== formData.password2 ? "Passwords don't match" : ""}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setUiState({ ...uiState, showConfirm: !uiState.showConfirm })} edge="end">
                      {uiState.showConfirm ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Divider sx={{ my: 1, opacity: 0.5 }}>Legal Agreements</Divider>

            <FormControlLabel
              control={
                <Checkbox
                  name="terms_accepted"
                  checked={formData.terms_accepted}
                  onChange={handleChange}
                  required
                  sx={{ color: colors.sage, '&.Mui-checked': { color: colors.sage } }}
                />
              }
              label={
                <Typography variant="body2" sx={{ color: colors.brown }}>
                  I accept the <Link to="/terms" style={{ color: colors.sage, fontWeight: 700 }}>Terms of Service</Link>
                </Typography>
              }
            />

            <FormControlLabel
              control={
                <Checkbox
                  name="privacy_policy_accepted"
                  checked={formData.privacy_policy_accepted}
                  onChange={handleChange}
                  required
                  sx={{ color: colors.sage, '&.Mui-checked': { color: colors.sage } }}
                />
              }
              label={
                <Typography variant="body2" sx={{ color: colors.brown }}>
                  I accept the <Link to="/privacy" style={{ color: colors.sage, fontWeight: 700 }}>Privacy Policy</Link>
                </Typography>
              }
            />

            <FormControlLabel
              control={
                <Checkbox
                  name="marketing_opt_in"
                  checked={formData.marketing_opt_in}
                  onChange={handleChange}
                  sx={{ color: colors.sage, '&.Mui-checked': { color: colors.sage } }}
                />
              }
              label={
                <Typography variant="body2" sx={{ color: colors.brown }}>
                  I want to receive updates and promotional emails from CareNest
                </Typography>
              }
            />

            <Button
              type="submit"
              variant="contained"
              fullWidth
              disabled={uiState.isLoading}
              sx={{
                py: 2,
                borderRadius: '16px',
                bgcolor: colors.brown,
                fontSize: '16px',
                fontWeight: 700,
                textTransform: 'none',
                '&:hover': { bgcolor: colors.charcoal },
                '&.Mui-disabled': { bgcolor: colors.taupe }
              }}
            >
              {uiState.isLoading ? <CircularProgress size={24} color="inherit" /> : 'Complete Registration'}
            </Button>
          </Stack>
        </form>

        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Typography variant="body2" sx={{ color: colors.taupe }}>
            Already part of the nest? <Link to="/login" style={{ color: colors.sage, fontWeight: 700, textDecoration: 'none' }}>Sign In</Link>
          </Typography>
        </Box>
      </RegisterPaper>
    </RegisterContainer>
  );
};

export default Register;