import { createTheme } from '@mui/material/styles';

// Your exact CareNest colors from logo
const carenestColors = {
  cream: '#F9F3E5',
  brown: '#8B735B',
  peach: '#E8C9AC',
  sage: '#8B9474',
  taupe: '#5E4E3E',
};

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: carenestColors.sage,       // Sage Green for primary actions
      light: '#A3AC90',
      dark: '#737A5F',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: carenestColors.peach,      // Soft Peach for secondary
      light: '#EDD9C4',
      dark: '#C99766',
      contrastText: carenestColors.brown,
    },
    neutral: {
      main: carenestColors.brown,      // Warm Brown for text
      light: '#A3927C',
      dark: '#735E4A',
      contrastText: '#FFFFFF',
    },
    background: {
      default: carenestColors.cream,   // Cream background
      paper: '#FFFFFF',
    },
    text: {
      primary: carenestColors.taupe,   // Deep Taupe for headings
      secondary: carenestColors.brown, // Warm Brown for body
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontFamily: '"Playfair Display", "Georgia", serif',
      fontWeight: 700,
      fontSize: '3rem',
      color: carenestColors.taupe,
    },
    h2: {
      fontFamily: '"Playfair Display", "Georgia", serif',
      fontWeight: 600,
      fontSize: '2.5rem',
      color: carenestColors.taupe,
    },
    h3: {
      fontFamily: '"Playfair Display", "Georgia", serif',
      fontWeight: 600,
      fontSize: '2rem',
      color: carenestColors.taupe,
    },
    h4: {
      fontFamily: '"Playfair Display", "Georgia", serif',
      fontWeight: 500,
      fontSize: '1.75rem',
      color: carenestColors.taupe,
    },
    h5: {
      fontFamily: '"Playfair Display", "Georgia", serif',
      fontWeight: 500,
      fontSize: '1.5rem',
      color: carenestColors.taupe,
    },
    h6: {
      fontFamily: '"Playfair Display", "Georgia", serif',
      fontWeight: 500,
      fontSize: '1.25rem',
      color: carenestColors.taupe,
    },
    body1: {
      fontFamily: '"Inter", sans-serif',
      fontSize: '1rem',
      lineHeight: 1.6,
      color: carenestColors.brown,
    },
    body2: {
      fontFamily: '"Inter", sans-serif',
      fontSize: '0.875rem',
      lineHeight: 1.5,
      color: carenestColors.brown,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          borderRadius: 10,
          padding: '10px 24px',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 6px 20px rgba(139, 116, 91, 0.15)',
          },
        },
        containedPrimary: {
          background: `linear-gradient(135deg, ${carenestColors.sage} 0%, #737A5F 100%)`,
          boxShadow: '0 4px 14px rgba(139, 148, 116, 0.4)',
        },
        containedSecondary: {
          background: `linear-gradient(135deg, ${carenestColors.peach} 0%, #D9B089 100%)`,
          color: carenestColors.brown,
          boxShadow: '0 4px 14px rgba(232, 201, 172, 0.4)',
        },
        outlinedPrimary: {
          borderColor: carenestColors.sage,
          color: carenestColors.sage,
          '&:hover': {
            backgroundColor: 'rgba(139, 148, 116, 0.08)',
            borderColor: carenestColors.sage,
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 8px 32px rgba(139, 116, 91, 0.08)',
          border: `1px solid ${carenestColors.cream}`,
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: '0 12px 48px rgba(139, 116, 91, 0.12)',
            transform: 'translateY(-4px)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 10,
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: carenestColors.peach,
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: carenestColors.sage,
              borderWidth: 2,
            },
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#FFFFFF',
          color: carenestColors.taupe,
          boxShadow: '0 2px 10px rgba(139, 116, 91, 0.05)',
        },
      },
    },
  },
});

// Add custom colors to theme
theme.palette.carenest = carenestColors;

export default theme;