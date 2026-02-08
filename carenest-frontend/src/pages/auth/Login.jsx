import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
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
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  ArrowForward,
} from '@mui/icons-material';
import styled from 'styled-components';
import { useAuth } from '../../contexts/AuthContext';
import { colors } from '../../components/ui/styled';

const LoginContainer = styled(Container)`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, ${colors.cream} 0%, ${colors.peach}20 100%);
  padding: 20px;
`;

const LoginPaper = styled(motion(Paper))`
  padding: 40px;
  border-radius: 20px;
  width: 100%;
  max-width: 450px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid ${colors.peach}30;
  box-shadow: 0 20px 60px rgba(139, 116, 91, 0.15);
`;

const LogoCircle = styled.div`
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, ${colors.sage} 0%, ${colors.peach} 100%);
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  color: white;
  font-weight: bold;
  font-size: 24px;
  box-shadow: 0 8px 20px rgba(139, 148, 116, 0.3);
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 30px;
`;

const StyledTextField = styled(TextField)`
  && {
    .MuiOutlinedInput-root {
      background: ${colors.cream};
      border-radius: 12px;
      
      &:hover .MuiOutlinedInput-notchedOutline {
        border-color: ${colors.peach};
      }
      
      &.Mui-focused .MuiOutlinedInput-notchedOutline {
        border-color: ${colors.sage};
        border-width: 2px;
      }
    }
    
    .MuiInputLabel-root {
      color: ${colors.brown};
      
      &.Mui-focused {
        color: ${colors.sage};
      }
    }
  }
`;

const SubmitButton = styled(Button)`
  && {
    background: linear-gradient(135deg, ${colors.sage} 0%, #737A5F 100%);
    color: white;
    font-weight: 600;
    padding: 14px;
    border-radius: 12px;
    text-transform: none;
    font-size: 16px;
    box-shadow: 0 4px 15px rgba(139, 148, 116, 0.3);
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(139, 148, 116, 0.4);
    }
    
    &:disabled {
      background: ${colors.brown}40;
    }
  }
`;

const SocialButton = styled(Button)`
  && {
    flex: 1;
    padding: 12px;
    border-radius: 12px;
    text-transform: none;
    font-weight: 500;
    border: 1px solid ${colors.peach}50;
    color: ${colors.taupe};
    background: white;
    transition: all 0.2s ease;
    
    &:hover {
      border-color: ${colors.sage};
      background: ${colors.sage}10;
    }
  }
`;

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { login, error } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    const result = await login(formData.email, formData.password);
    
    if (!result.success) {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    // Implement Google OAuth with Django
    window.location.href = 'http://localhost:8000/api/auth/google/';
  };

  const handleFacebookLogin = () => {
    // Implement Facebook OAuth with Django
    window.location.href = 'http://localhost:8000/api/auth/facebook/';
  };

  return (
    <LoginContainer maxWidth={false}>
      <LoginPaper
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Logo */}
        <Box sx={{ textAlign: 'center', mb: 3 }}>
          <LogoCircle>CN</LogoCircle>
          <Typography variant="h4" sx={{ color: colors.taupe, fontWeight: 700, mb: 1 }}>
            Welcome Back
          </Typography>
          <Typography variant="body1" sx={{ color: colors.brown }}>
            Sign in to your CareNest account
          </Typography>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
            {typeof error === 'object' ? JSON.stringify(error) : error}
          </Alert>
        )}

        <Form onSubmit={handleSubmit}>
          {/* Email */}
          <StyledTextField
            fullWidth
            label="Email Address"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            required
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Email sx={{ color: colors.brown }} />
                </InputAdornment>
              ),
            }}
          />

          {/* Password */}
          <StyledTextField
            fullWidth
            label="Password"
            name="password"
            type={showPassword ? 'text' : 'password'}
            value={formData.password}
            onChange={handleChange}
            required
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Lock sx={{ color: colors.brown }} />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => setShowPassword(!showPassword)}
                    edge="end"
                  >
                    {showPassword ? (
                      <VisibilityOff sx={{ color: colors.brown }} />
                    ) : (
                      <Visibility sx={{ color: colors.brown }} />
                    )}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          {/* Remember Me & Forgot Password */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <FormControlLabel
              control={
                <Checkbox
                  name="rememberMe"
                  checked={formData.rememberMe}
                  onChange={handleChange}
                  sx={{
                    color: colors.sage,
                    '&.Mui-checked': { color: colors.sage },
                  }}
                />
              }
              label="Remember me"
              sx={{ color: colors.brown }}
            />
            <Button
              component={Link}
              to="/forgot-password"
              sx={{ color: colors.sage, textTransform: 'none' }}
            >
              Forgot password?
            </Button>
          </Box>

          {/* Submit Button */}
          <SubmitButton
            type="submit"
            fullWidth
            disabled={isLoading}
            endIcon={!isLoading && <ArrowForward />}
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </SubmitButton>
        </Form>

        {/* Divider */}
        <Box sx={{ my: 3 }}>
          <Divider>
            <Typography variant="body2" sx={{ color: colors.brown, px: 2 }}>
              Or continue with
            </Typography>
          </Divider>
        </Box>

        {/* Social Login */}
        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <SocialButton
            fullWidth
            startIcon={
              <Box component="img" src="/google.svg" sx={{ width: 20, height: 20 }} />
            }
            onClick={handleGoogleLogin}
          >
            Google
          </SocialButton>
          <SocialButton
            fullWidth
            startIcon={
              <Box component="img" src="/facebook.svg" sx={{ width: 20, height: 20 }} />
            }
            onClick={handleFacebookLogin}
          >
            Facebook
          </SocialButton>
        </Box>

        {/* Sign Up Link */}
        <Box sx={{ textAlign: 'center', mt: 3, pt: 3, borderTop: `1px solid ${colors.peach}30` }}>
          <Typography variant="body2" sx={{ color: colors.brown, mb: 1 }}>
            Don't have an account?
          </Typography>
          <Button
            component={Link}
            to="/register"
            variant="outlined"
            sx={{
              borderColor: colors.sage,
              color: colors.sage,
              '&:hover': {
                borderColor: colors.sage,
                backgroundColor: `${colors.sage}10`,
              },
            }}
          >
            Create Account
          </Button>
        </Box>

        {/* Back to Home */}
        <Box sx={{ textAlign: 'center', mt: 3 }}>
          <Button
            component={Link}
            to="/"
            sx={{ color: colors.brown, textTransform: 'none' }}
          >
            ← Back to home
          </Button>
        </Box>
      </LoginPaper>
    </LoginContainer>
  );
};

export default Login;