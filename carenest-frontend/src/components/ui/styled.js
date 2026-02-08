import styled from 'styled-components';
import { Card, Button, TextField, Box } from '@mui/material';

// Export CareNest colors for easy access
export const colors = {
  cream: '#F9F3E5',
  brown: '#8B735B',
  peach: '#E8C9AC',
  sage: '#8B9474',
  taupe: '#5E4E3E',
};

// Styled Card variations
export const StyledCard = styled(Card)`
  background: ${({ variant }) => 
    variant === 'peach' ? 'rgba(232, 201, 172, 0.2)' : 
    variant === 'sage' ? 'rgba(139, 148, 116, 0.1)' : 
    '#FFFFFF'};
  border: ${({ variant }) => 
    variant === 'peach' ? `1px solid ${colors.peach}` : 
    variant === 'sage' ? `1px solid ${colors.sage}` : 
    `1px solid ${colors.cream}`};
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    transform: ${({ hoverable }) => hoverable ? 'translateY(-8px)' : 'none'};
    box-shadow: ${({ hoverable }) => 
      hoverable ? '0 20px 40px rgba(139, 116, 91, 0.15)' : 'none'};
  }
`;

// Styled Button variations
export const StyledButton = styled(Button)`
  && {
    font-weight: 600;
    border-radius: 10px;
    text-transform: none;
    padding: ${({ size }) => 
      size === 'large' ? '14px 32px' : 
      size === 'small' ? '8px 16px' : 
      '10px 24px'};
    font-size: ${({ size }) => 
      size === 'large' ? '1.1rem' : 
      size === 'small' ? '0.875rem' : 
      '1rem'};
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(139, 148, 116, 0.3);
    }

    &:active {
      transform: translateY(0);
    }
  }
`;

// Glassmorphism container
export const GlassCard = styled.div`
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 32px;
  box-shadow: 0 8px 32px rgba(139, 116, 91, 0.1);
`;

// Gradient button
export const GradientButton = styled(StyledButton)`
  && {
    background: linear-gradient(
      135deg,
      ${colors.sage} 0%,
      ${colors.peach} 100%
    );
    color: white;
    border: none;
    position: relative;
    overflow: hidden;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(
        90deg,
        transparent,
        rgba(255, 255, 255, 0.2),
        transparent
      );
      transition: left 0.5s ease;
    }

    &:hover::before {
      left: 100%;
    }
  }
`;

// Input with custom styling
export const StyledInput = styled(TextField)`
  && {
    .MuiOutlinedInput-root {
      background: ${colors.cream};
      border-radius: 10px;
      
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

// Flex container with responsive design
export const FlexContainer = styled(Box)`
  display: flex;
  gap: ${({ gap }) => gap || '16px'};
  flex-direction: ${({ direction }) => direction || 'row'};
  align-items: ${({ align }) => align || 'center'};
  justify-content: ${({ justify }) => justify || 'flex-start'};
  flex-wrap: ${({ wrap }) => wrap || 'nowrap'};
  
  @media (max-width: 768px) {
    flex-direction: ${({ mobileDirection }) => mobileDirection || 'column'};
    gap: ${({ mobileGap }) => mobileGap || '12px'};
  }
`;

// Page container
export const PageContainer = styled(Box)`
  min-height: 100vh;
  background: ${colors.cream};
  padding: ${({ noPadding }) => noPadding ? '0' : '20px'};
  
  @media (max-width: 768px) {
    padding: ${({ noPadding }) => noPadding ? '0' : '16px'};
  }
`;