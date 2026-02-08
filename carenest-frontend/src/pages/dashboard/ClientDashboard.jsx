/**
 * CareNest Pro - Premium Client Discovery Dashboard
 * Version: 4.2.6 - Bio Limited to 3 Words on Small Devices
 * * CHANGE LOG:
 * - ADDED: Bio text limited to 3 words on small devices
 * - IMPROVED: Smart text truncation for mobile
 * - OPTIMIZED: Word count limit for better mobile experience
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Container, Typography, Box, Button, Grid, Avatar, 
  Chip, Stack, TextField, InputAdornment, Skeleton, 
  Rating, Divider, IconButton, Badge, Slider, 
  FormControlLabel, Checkbox, MenuItem, Select,
  FormControl, InputLabel, Dialog, DialogTitle, 
  DialogContent, DialogActions, CircularProgress, 
  Alert, Snackbar, Paper, Tooltip, Zoom, Fade,
  List, ListItem, ListItemIcon, ListItemText,
  useMediaQuery, useTheme
} from '@mui/material';
import {
  Search, LocationOn, Star, Verified, FavoriteBorder, 
  Favorite, Info, ShieldMoon, Refresh, ErrorOutline,
  KeyboardArrowRight, Tune, CalendarMonth, LocalOffer,
  WorkHistory, GppGood, WorkspacePremium, AccessTime,
  HomeWork, HealthAndSafety, AutoAwesome, Psychology,
  SelfImprovement, VerifiedUser, Security, Payments,
  Navigation, Sort, FilterList, MoreVert
} from '@mui/icons-material';
import { styled, alpha } from '@mui/material/styles';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import Navbar from '../../components/layout/Navbar';

// IMPORTING ACTUAL API SERVICES
import { searchAPI, appointmentsAPI } from '../../services/api';

// =============================================================================
// 1. BRANDING & STYLE SYSTEM
// =============================================================================

const COLORS = {
  sage: '#8DA399',
  taupe: '#8B745B',
  peach: '#F8D7C4',
  cream: '#FDFBF7',
  brown: '#5D4A3E',
  charcoal: '#2D2D2D',
  white: '#FFFFFF',
  border: 'rgba(139, 116, 91, 0.15)',
  success: '#2D5A27',
  error: '#A34D4D'
};

/**
 * Premium Profile Card with Advanced Hover States
 */
const ProfileCard = styled(motion.div)(({ theme }) => ({
  background: COLORS.white,
  borderRadius: '20px',
  border: `1px solid ${COLORS.border}`,
  padding: '20px',
  position: 'relative',
  cursor: 'pointer',
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    transform: 'translateY(-8px)',
    boxShadow: '0 20px 40px -8px rgba(93, 74, 62, 0.12)',
    borderColor: COLORS.sage
  },
  // For desktop/tablet (sm and up): full width
  width: '100%',
  // Only on mobile (xs): fixed 180px width
  [theme.breakpoints.only('xs')]: {
    padding: '16px',
    borderRadius: '16px',
    width: '180px' // Fixed width ONLY on extra small screens
  }
}));

/**
 * Filter Panel with Frosted Glass Effect
 */
const GlassPanel = styled(Box)(({ theme }) => ({
  background: 'rgba(255, 255, 255, 0.9)',
  backdropFilter: 'blur(12px)',
  borderRadius: '20px',
  border: `1px solid ${COLORS.border}`,
  padding: '24px',
  position: 'sticky',
  top: '100px',
  boxShadow: '0 4px 20px rgba(0,0,0,0.02)',
  [theme.breakpoints.down('lg')]: {
    position: 'relative',
    top: 0,
    marginBottom: '24px'
  }
}));

const StatBox = styled(Box)({
  background: COLORS.cream,
  borderRadius: '12px',
  padding: '10px 14px',
  display: 'flex',
  alignItems: 'center',
  gap: '10px',
  border: `1px solid ${alpha(COLORS.taupe, 0.1)}`
});

const PremiumButton = styled(Button)(({ variant }) => ({
  borderRadius: '12px',
  padding: '10px 20px',
  fontWeight: 600,
  textTransform: 'none',
  fontSize: '0.9rem',
  boxShadow: 'none',
  transition: 'all 0.3s ease',
  backgroundColor: variant === 'contained' ? COLORS.brown : 'transparent',
  color: variant === 'contained' ? COLORS.white : COLORS.brown,
  border: variant === 'outlined' ? `2px solid ${COLORS.brown}` : 'none',
  '&:hover': {
    backgroundColor: variant === 'contained' ? COLORS.charcoal : alpha(COLORS.brown, 0.05),
    transform: 'scale(1.02)',
    boxShadow: variant === 'contained' ? '0 8px 20px rgba(93, 74, 62, 0.2)' : 'none'
  }
}));

const StyledBadge = styled(Badge)(({ theme }) => ({
  '& .MuiBadge-badge': {
    backgroundColor: '#44b700',
    color: '#44b700',
    boxShadow: `0 0 0 2px ${theme.palette.background.paper}`,
    '&::after': {
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      borderRadius: '50%',
      animation: 'ripple 1.2s infinite ease-in-out',
      border: '1px solid currentColor',
      content: '""',
    },
  },
  '@keyframes ripple': {
    '0%': { transform: 'scale(.8)', opacity: 1 },
    '100%': { transform: 'scale(2.4)', opacity: 0 },
  },
}));

// =============================================================================
// 2. DISCOVERY ENGINE LOGIC
// =============================================================================

const ClientDashboard = () => {
  const { user } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'md'));
  const isDesktop = useMediaQuery(theme.breakpoints.up('lg'));
  
  // -- Discovery State --
  const [caregivers, setCaregivers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  const [selectedProvider, setSelectedProvider] = useState(null);
  
  // -- Filter & Booking State --
  const [searchQuery, setSearchQuery] = useState('');
  const [rateRange, setRateRange] = useState([20, 150]);
  const [experience, setExperience] = useState('');
  const [specialty, setSpecialty] = useState('');
  const [sortBy, setSortBy] = useState('recommended');
  const [isBooking, setIsBooking] = useState(false);
  
  // -- Appointment Details (Draft state for Modal) --
  const [bookingDate, setBookingDate] = useState(new Date().toISOString().split('T')[0]);
  const [bookingTime, setBookingTime] = useState("09:00");
  const [serviceType, setServiceType] = useState("General Care");
  const [bookingNotes, setBookingNotes] = useState("");

  /**
   * Helper function to truncate text to specific number of words
   */
  const truncateToWords = (text, maxWords = 3) => {
    if (!text) return "Professional caregiver...";
    
    const words = text.split(' ');
    if (words.length <= maxWords) return text;
    
    return words.slice(0, maxWords).join(' ') + '...';
  };

  /**
   * Helper function to truncate text for mobile (3 words) and desktop (1 line)
   */
  const getTruncatedBio = (bio, isMobileDevice) => {
    if (isMobileDevice) {
      return truncateToWords(bio, 3);
    }
    // For desktop/tablet: keep the 1-line ellipsis
    return bio || "Professional caregiver dedicated to providing compassionate support.";
  };

  /**
   * RE-SYNC WITH SEARCH API
   */
  const syncCaregivers = useCallback(async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const filters = {
        search: searchQuery,
        min_rate: rateRange[0],
        max_rate: rateRange[1],
        experience_years: experience,
        specialty: specialty,
        sort: sortBy
      };

      const data = await searchAPI.searchCaregivers(filters);
      // Backend returns { results: [...] } or just [...] depending on pagination
      const results = data.results || data;
      setCaregivers(Array.isArray(results) ? results : []);
    } catch (err) {
      console.error("Discovery Error:", err);
      setErrorMsg("Unable to synchronize care providers. Please verify your network connection.");
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, rateRange, experience, specialty, sortBy]);

  useEffect(() => {
    const timer = setTimeout(() => syncCaregivers(), 400);
    return () => clearTimeout(timer);
  }, [syncCaregivers]);

  /**
   * BOOKING EXECUTION - Aligned with Enterprise Schema v5.0.0
   * FIX: Robust Error Parsing for Missing Client Profile
   * CRITICAL FIX: Added duration_hours field to prevent backend multiplication error
   */
  const handleBooking = async () => {
    if (!selectedProvider) return;
    setIsBooking(true);
    setErrorMsg(null);

    try {
      // Calculate End Time (2-hour default duration logic)
      const startTimeArr = bookingTime.split(':');
      const startHour = parseInt(startTimeArr[0]);
      const endHour = ((startHour + 2) % 24).toString().padStart(2, '0');
      const endTime = `${endHour}:${startTimeArr[1]}`;
      
      // CRITICAL FIX: Add duration_hours field (default 2 hours)
      const durationHours = 2.0;

      // Payload strictly following the Django Appointment Model
      const payload = {
        caregiver: selectedProvider.id,
        service_type: serviceType, 
        date: bookingDate,
        start_time: bookingTime,
        end_time: endTime,
        duration_hours: durationHours, // REQUIRED FIELD: Prevents backend multiplication error
        hourly_rate_at_booking: selectedProvider.hourly_rate,
        notes_to_caregiver: bookingNotes || `Booking requested via Discovery Dashboard by ${user?.username || 'Client'}`,
        status: 'pending'
      };

      console.log("DEBUG: Booking payload:", JSON.stringify(payload, null, 2));
      
      await appointmentsAPI.createAppointment(payload);
      setSuccessMsg(`Your booking request has been sent to ${selectedProvider.first_name}!`);
      setSelectedProvider(null);
      setBookingNotes(""); // Reset notes
    } catch (err) {
      const serverErrors = err.response?.data;
      console.error("Booking Error Detail:", serverErrors);

      // SPECIFIC FIX: Parse the 'client' key from the 400 Bad Request
      if (serverErrors && serverErrors.client) {
        const msg = Array.isArray(serverErrors.client) ? serverErrors.client[0] : serverErrors.client;
        setErrorMsg(`Account Restriction: ${msg}`);
      } else if (serverErrors) {
        // Fallback for other validation errors
        const genericMsg = Object.entries(serverErrors)
          .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(' ') : value}`)
          .join(' | ');
        setErrorMsg(genericMsg);
      } else {
        setErrorMsg("Booking failed. Ensure you are logged in with a Client account.");
      }
    } finally {
      setIsBooking(false);
    }
  };

  /**
   * Internal Helper: Calculate completion percentage for UI
   */
  const getMatchScore = (provider) => {
    let score = 90;
    if (provider.experience_years > 5) score += 5;
    if (provider.average_rating > 4.8) score += 5;
    return score > 100 ? 100 : score;
  };

  /**
   * Format hourly rate for display
   */
  const formatHourlyRate = (rate) => {
    if (typeof rate === 'number') {
      return `R${rate.toFixed(2)}`;
    }
    return `R${parseFloat(rate || 25).toFixed(2)}`;
  };

  /**
   * Calculate total cost for display
   */
  const calculateTotalCost = (hourlyRate, hours = 2) => {
    const rate = typeof hourlyRate === 'number' ? hourlyRate : parseFloat(hourlyRate || 25);
    return (rate * hours).toFixed(2);
  };

  // Calculate responsive grid columns
  const getGridColumns = () => {
    if (isMobile) return 4; // 3 items per row (12/4 = 3)
    if (isTablet) return 6; // 2 items per row (12/6 = 2)
    return 4; // 3 items per row on desktop (12/4 = 3)
  };

  // ===========================================================================
  // 3. UI RENDERING
  // ===========================================================================

  return (
    <Box sx={{ bgcolor: COLORS.cream, minHeight: '100vh', pb: 6, overflowX: 'hidden' }}>
      <Navbar />
      
      {/* Hero Header Section - COMPACT VERSION */}
      <Box sx={{ 
        pt: { xs: 12, md: 16 }, 
        pb: { xs: 6, md: 8 }, 
        background: `linear-gradient(180deg, ${alpha(COLORS.peach, 0.4)} 0%, ${COLORS.cream} 100%)`,
        borderBottom: `1px solid ${COLORS.border}`
      }}>
        <Container maxWidth="xl">
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={7}>
              <motion.div initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }}>
                <Typography variant="overline" sx={{ 
                  letterSpacing: { xs: 2, md: 4 }, 
                  color: COLORS.taupe, 
                  fontWeight: 900,
                  fontSize: { xs: '0.7rem', md: '0.8rem' }
                }}>
                  ESTABLISHED 2026
                </Typography>
                <Typography variant="h1" sx={{ 
                  fontWeight: 800, 
                  color: COLORS.brown, 
                  fontSize: { xs: '2rem', sm: '2.5rem', md: '3.5rem' },
                  lineHeight: 1.2,
                  mb: 2,
                  letterSpacing: '-1px'
                }}>
                  Discovery{' '}
                  <span style={{ color: COLORS.sage }}>Engine.</span>
                </Typography>
                <Typography variant="h6" sx={{ 
                  color: COLORS.taupe, 
                  maxWidth: 600, 
                  mb: 3, 
                  fontWeight: 400, 
                  lineHeight: 1.5,
                  fontSize: { xs: '1rem', md: '1.25rem' }
                }}>
                  Curating elite caregivers for {user?.firstName || 'our members'}. 
                  Every professional is background-checked and verified.
                </Typography>
                
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                   <StatBox>
                      <VerifiedUser sx={{ color: COLORS.sage, fontSize: { xs: 20, md: 24 } }} />
                      <Box>
                        <Typography variant="body2" fontWeight={600}>100% Verified</Typography>
                        <Typography variant="caption" color="textSecondary">Staff Screening</Typography>
                      </Box>
                   </StatBox>
                   <StatBox>
                      <Security sx={{ color: COLORS.sage, fontSize: { xs: 20, md: 24 } }} />
                      <Box>
                        <Typography variant="body2" fontWeight={600}>Secured Escrow</Typography>
                        <Typography variant="caption" color="textSecondary">Protected Payments</Typography>
                      </Box>
                   </StatBox>
                </Stack>
              </motion.div>
            </Grid>
            <Grid item xs={12} md={5}>
              <motion.div 
                initial={{ opacity: 0, y: 20 }} 
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <TextField 
                  fullWidth
                  placeholder="Search by name, specialty, or city..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  sx={{ 
                    '& .MuiOutlinedInput-root': { 
                      height: { xs: 60, md: 70 },
                      borderRadius: '20px', 
                      bgcolor: 'white',
                      fontSize: { xs: '1rem', md: '1.1rem' },
                      boxShadow: '0 10px 30px rgba(0,0,0,0.05)',
                      '& fieldset': { borderColor: 'transparent' },
                      '&:hover fieldset': { borderColor: COLORS.sage }
                    } 
                  }}
                  InputProps={{
                    startAdornment: <InputAdornment position="start" sx={{ ml: { xs: 1, md: 2 } }}>
                      <Search sx={{ fontSize: { xs: 24, md: 28 }, color: COLORS.sage }} />
                    </InputAdornment>,
                  }}
                />
              </motion.div>
            </Grid>
          </Grid>
        </Container>
      </Box>

      <Container maxWidth="xl" sx={{ mt: { xs: 3, md: 4 } }}>
        {/* Error Alert Overlay */}
        <AnimatePresence>
          {errorMsg && (
            <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
              <Alert 
                severity="error" 
                variant="filled"
                sx={{ 
                  mb: 3, 
                  borderRadius: '16px', 
                  py: 1, 
                  bgcolor: COLORS.error,
                  boxShadow: '0 8px 24px rgba(163, 77, 77, 0.3)'
                }} 
                onClose={() => setErrorMsg(null)}
                action={
                  <Button color="inherit" size="small" onClick={() => window.location.href='/profile-settings'}>
                    FIX PROFILE
                  </Button>
                }
              >
                <Typography fontWeight={600} fontSize="0.9rem">{errorMsg}</Typography>
              </Alert>
            </motion.div>
          )}
        </AnimatePresence>

        <Grid container spacing={3}>
          {/* FILTER SIDEBAR */}
          {isDesktop && (
            <Grid item lg={3}>
              <GlassPanel>
                <Stack spacing={3}>
                  <Box>
                    <Typography variant="h6" fontWeight={700} sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1.5 }}>
                      <Tune sx={{ color: COLORS.sage, fontSize: 20 }} /> Refine Search
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                  </Box>

                  <Box>
                    <Typography variant="caption" fontWeight={700} color="textSecondary" sx={{ mb: 1, display: 'block', textTransform: 'uppercase', letterSpacing: 1 }}>
                      Hourly Rate Range
                    </Typography>
                    <Slider 
                      value={rateRange} 
                      min={15} max={250} 
                      onChange={(e, v) => setRateRange(v)}
                      sx={{ 
                        color: COLORS.sage,
                        '& .MuiSlider-thumb': { height: 20, width: 20, bgcolor: 'white', border: `2px solid ${COLORS.sage}` }
                      }}
                      valueLabelDisplay="auto"
                    />
                    <Stack direction="row" justifyContent="space-between">
                      <Typography variant="body2" fontWeight={600}>R{rateRange[0]}</Typography>
                      <Typography variant="body2" fontWeight={600}>R{rateRange[1]}+</Typography>
                    </Stack>
                  </Box>

                  <FormControl fullWidth variant="filled" size="small">
                    <InputLabel>Experience Level</InputLabel>
                    <Select 
                      value={experience} 
                      label="Experience Level" 
                      onChange={(e) => setExperience(e.target.value)}
                      sx={{ borderRadius: '10px', bgcolor: 'white' }}
                      disableUnderline
                    >
                      <MenuItem value="">All Levels</MenuItem>
                      <MenuItem value="2">Junior (2+ Years)</MenuItem>
                      <MenuItem value="5">Intermediate (5+ Years)</MenuItem>
                      <MenuItem value="10">Expert (10+ Years)</MenuItem>
                    </Select>
                  </FormControl>

                  <FormControl fullWidth variant="filled" size="small">
                    <InputLabel>Care Specialty</InputLabel>
                    <Select 
                      value={specialty} 
                      onChange={(e) => setSpecialty(e.target.value)}
                      sx={{ borderRadius: '10px', bgcolor: 'white' }}
                      disableUnderline
                    >
                      <MenuItem value="">Any Specialty</MenuItem>
                      <MenuItem value="Elderly">Elderly Care</MenuItem>
                      <MenuItem value="Pediatric">Pediatric Care</MenuItem>
                      <MenuItem value="Post-Op">Post-Op Recovery</MenuItem>
                      <MenuItem value="Dementia">Dementia Expert</MenuItem>
                    </Select>
                  </FormControl>

                  <Box>
                    <Typography variant="caption" fontWeight={700} color="textSecondary" sx={{ mb: 1, display: 'block', textTransform: 'uppercase', letterSpacing: 1 }}>
                      Trust & Safety
                    </Typography>
                    <Stack spacing={0.5}>
                      <FormControlLabel control={<Checkbox defaultChecked size="small" sx={{ color: COLORS.sage }} />} label={<Typography variant="body2">Background Checked</Typography>} />
                      <FormControlLabel control={<Checkbox size="small" sx={{ color: COLORS.sage }} />} label={<Typography variant="body2">First Aid Certified</Typography>} />
                      <FormControlLabel control={<Checkbox size="small" sx={{ color: COLORS.sage }} />} label={<Typography variant="body2">Immediate Availability</Typography>} />
                    </Stack>
                  </Box>

                  <PremiumButton variant="outlined" fullWidth onClick={() => {
                    setSearchQuery('');
                    setRateRange([20, 150]);
                    setExperience('');
                    setSpecialty('');
                  }}>
                    Reset All Filters
                  </PremiumButton>
                </Stack>
              </GlassPanel>
            </Grid>
          )}

          {/* MAIN RESULTS AREA */}
          <Grid item xs={12} lg={9}>
            <Box sx={{ 
              mb: 3, 
              display: 'flex', 
              flexDirection: { xs: 'column', sm: 'row' }, 
              justifyContent: 'space-between', 
              alignItems: { xs: 'flex-start', sm: 'center' },
              gap: 2
            }}>
              <Typography variant="h6" fontWeight={700} color={COLORS.brown}>
                {caregivers.length} Professionals Found
              </Typography>
              <Stack direction="row" spacing={2} alignItems="center">
                {!isDesktop && (
                  <PremiumButton 
                    variant="outlined" 
                    startIcon={<FilterList />}
                    onClick={() => {
                      // Mobile filter dialog can be implemented here
                      alert('Mobile filter dialog would open here');
                    }}
                  >
                    Filters
                  </PremiumButton>
                )}
                <Typography variant="body2" color="textSecondary" fontWeight={600}>SORT BY:</Typography>
                <Select 
                  size="small" 
                  value={sortBy} 
                  onChange={(e) => setSortBy(e.target.value)}
                  sx={{ 
                    borderRadius: '8px', 
                    bgcolor: 'white', 
                    fontWeight: 600,
                    minWidth: 150 
                  }}
                >
                  <MenuItem value="recommended">Recommended</MenuItem>
                  <MenuItem value="rate_low">Lowest Rate</MenuItem>
                  <MenuItem value="rating">Top Rated</MenuItem>
                  <MenuItem value="experience">Most Experienced</MenuItem>
                </Select>
              </Stack>
            </Box>

            {/* RESPONSIVE RESULTS GRID - 3 per row on mobile */}
            <Grid container spacing={2}>
              {isLoading ? (
                Array.from(new Array(6)).map((_, i) => (
                  <Grid item xs={4} sm={4} md={4} key={i}>
                    <Skeleton 
                      variant="rectangular" 
                      height={300} 
                      sx={{ 
                        borderRadius: '20px',
                        height: { xs: 280, sm: 320, md: 340 }
                      }} 
                    />
                  </Grid>
                ))
              ) : caregivers.length > 0 ? (
                caregivers.map((provider) => (
                  <Grid item xs={4} sm={4} md={4} key={provider.id}>
                    <ProfileCard 
                      initial={{ opacity: 0, y: 20 }} 
                      animate={{ opacity: 1, y: 0 }}
                      whileHover={{ scale: 1.02 }}
                      onClick={() => setSelectedProvider(provider)}
                    >
                      {/* Top Header Row - COMPACT */}
                      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                        <StyledBadge overlap="circular" anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }} variant="dot">
                          <Avatar 
                            src={provider.profile_image} 
                            sx={{ 
                              width: { xs: 60, sm: 70, md: 80 }, 
                              height: { xs: 60, sm: 70, md: 80 }, 
                              border: `3px solid ${COLORS.peach}`, 
                              boxShadow: '0 5px 15px rgba(0,0,0,0.1)' 
                            }} 
                          />
                        </StyledBadge>
                        <Box sx={{ textAlign: 'right' }}>
                          <Chip 
                            label={formatHourlyRate(provider.hourly_rate)} 
                            sx={{ 
                              fontWeight: 700, 
                              bgcolor: COLORS.peach, 
                              color: COLORS.brown, 
                              fontSize: { xs: '0.8rem', md: '0.9rem' }, 
                              height: { xs: 28, md: 32 }, 
                              px: 1 
                            }} 
                          />
                          <Typography variant="caption" sx={{ display: 'block', mt: 0.5, fontWeight: 700, color: COLORS.sage, fontSize: '0.7rem' }}>
                            MATCH: {getMatchScore(provider)}%
                          </Typography>
                        </Box>
                      </Stack>

                      {/* Content Section */}
                      <Box sx={{ flexGrow: 1 }}>
                        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                          <Typography variant="h6" fontWeight={700} color={COLORS.brown} sx={{ fontSize: { xs: '1rem', md: '1.1rem' } }}>
                            {provider.first_name} {provider.last_name}
                          </Typography>
                          <GppGood sx={{ color: COLORS.sage, fontSize: { xs: 18, md: 20 } }} />
                        </Stack>
                        
                        <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1.5 }}>
                          <Rating 
                            value={provider.average_rating || 5} 
                            precision={0.1} 
                            readOnly 
                            size="small" 
                            sx={{ fontSize: { xs: '1rem', md: '1.1rem' } }}
                          />
                          <Typography variant="body2" fontWeight={700} sx={{ fontSize: '0.8rem' }}>
                            ({provider.total_reviews || 0})
                          </Typography>
                        </Stack>

                        {/* BIO TEXT - 3 WORDS ON MOBILE, 1 LINE ON DESKTOP */}
                        <Typography variant="body2" color="textSecondary" sx={{ 
                          mb: 2, 
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          WebkitLineClamp: 1,
                          whiteSpace: 'nowrap',
                          lineHeight: 1.4,
                          fontSize: { xs: '0.8rem', md: '0.9rem' },
                          width: '180px'
                        }}>
                          {isMobile 
                            ? truncateToWords(provider.bio || "Professional caregiver dedicated to providing compassionate support.", 3)
                            : (provider.bio || "Professional caregiver dedicated to providing compassionate support.")}
                        </Typography>

                        <Stack direction="row" flexWrap="wrap" gap={0.5} sx={{ mb: 3 }}>
                          <Chip 
                            icon={<LocationOn sx={{ fontSize: '12px !important' }} />} 
                            label={provider.city || 'Local'} 
                            size="small" 
                            variant="outlined" 
                            sx={{ fontSize: '0.7rem' }}
                          />
                          <Chip 
                            icon={<WorkHistory sx={{ fontSize: '12px !important' }} />} 
                            label={`${provider.experience_years}y`} 
                            size="small" 
                            variant="outlined" 
                            sx={{ fontSize: '0.7rem' }}
                          />
                          <Chip 
                            icon={<WorkspacePremium sx={{ fontSize: '12px !important' }} />} 
                            label="Elite" 
                            size="small" 
                            variant="outlined" 
                            sx={{ fontSize: '0.7rem' }}
                          />
                        </Stack>
                      </Box>

                      <Divider sx={{ mb: 2 }} />

                      {/* Action Row */}
                      <Stack direction="row" spacing={1}>
                        <PremiumButton variant="contained" fullWidth sx={{ fontSize: { xs: '0.8rem', md: '0.9rem' } }}>
                          View Profile
                        </PremiumButton>
                        <IconButton sx={{ 
                          border: `1px solid ${COLORS.border}`, 
                          borderRadius: '10px',
                          padding: { xs: '8px', md: '10px' }
                        }}>
                          <FavoriteBorder sx={{ fontSize: { xs: 18, md: 20 } }} />
                        </IconButton>
                      </Stack>
                    </ProfileCard>
                  </Grid>
                ))
              ) : (
                <Grid item xs={12}>
                  <Box sx={{ textAlign: 'center', py: 6 }}>
                    <ErrorOutline sx={{ fontSize: 60, color: COLORS.taupe, mb: 2 }} />
                    <Typography variant="h5" fontWeight={700} color={COLORS.brown}>No Providers Found</Typography>
                    <Typography variant="body1" color="textSecondary" sx={{ mt: 1 }}>
                      Try adjusting your filters or search terms.
                    </Typography>
                  </Box>
                </Grid>
              )}
            </Grid>
          </Grid>
        </Grid>
      </Container>

      {/* BOOKING MODAL */}
      <Dialog 
        open={Boolean(selectedProvider)} 
        onClose={() => setSelectedProvider(null)}
        fullWidth 
        maxWidth="md"
        TransitionComponent={Zoom}
        PaperProps={{ 
          sx: { 
            borderRadius: '24px', 
            p: { xs: 2, md: 3 }, 
            background: COLORS.white,
            boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
            m: { xs: 2, md: 3 }
          } 
        }}
      >
        {selectedProvider && (
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
              <Box>
                <Typography variant="h4" fontWeight={700} paddingBottom={'20px'} color={COLORS.brown}>Secure Booking</Typography>
                <Typography variant="subtitle2" fontWeight={700} color="textSecondary" sx={{ mb: 1, textTransform: 'uppercase' }}>About {selectedProvider.first_name}</Typography>
                <Typography variant="body2" color="textSecondary" sx={{ lineHeight: 1.6,mb: 2 }}> {selectedProvider.bio || "Professional caregiver dedicated to providing compassionate, high-quality support..."} </Typography>
              </Box>


              <IconButton onClick={() => setSelectedProvider(null)} size="small"><ErrorOutline /></IconButton>
            </Box>

            <Grid container spacing={3}>
              <Grid item xs={12} md={5}>
                <Box sx={{ position: 'relative' }}>
                  <Avatar 
                    src={selectedProvider.profile_image} 
                    sx={{ 
                      width: '100%', 
                      height: 'auto', 
                      aspectRatio: '1/1', 
                      borderRadius: '20px' 
                    }} 
                  />
                  <Box sx={{ 
                    position: 'absolute', 
                    bottom: -15, 
                    left: '50%', 
                    transform: 'translateX(-50%)',
                    bgcolor: COLORS.white, 
                    px: 2, 
                    py: 0.5, 
                    borderRadius: '12px', 
                    boxShadow: '0 5px 20px rgba(0,0,0,0.1)', 
                    border: `1px solid ${COLORS.border}`
                  }}>
                    <Typography variant="body1" fontWeight={700} color={COLORS.sage}>
                      {formatHourlyRate(selectedProvider.hourly_rate)}
                    </Typography>
                  </Box>
                </Box>
                
                <Box sx={{ mt: 4 }}>
                  <Typography variant="subtitle2" fontWeight={700} color="textSecondary" sx={{ mb: 1, textTransform: 'uppercase' }}>
                    Specialized In
                  </Typography>
                  <List dense>
                    {['', '', ''].map((item) => (
                      <ListItem key={item} sx={{ px: 0 }}>
                        <ListItemIcon sx={{ minWidth: 30 }}><AutoAwesome sx={{ color: COLORS.sage, fontSize: 16 }} /></ListItemIcon>
                        <ListItemText primary={<Typography variant="body2" fontWeight={600}>{item}</Typography>} />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              </Grid>

              <Grid item xs={12} md={7}>
                <Stack spacing={2}>
                  <Box>
                    <Typography variant="h6" fontWeight={700} sx={{ mb: 1 }}>Appointment Details</Typography>
                    <Grid container spacing={1.5}>
                      <Grid item xs={6}>
                        <TextField 
                          type="date" 
                          label="Service Date" 
                          fullWidth 
                          size="small"
                          value={bookingDate} 
                          onChange={(e) => setBookingDate(e.target.value)}
                          InputLabelProps={{ shrink: true }}
                          variant="filled" 
                          sx={{ '& .MuiFilledInput-root': { borderRadius: '10px', bgcolor: COLORS.cream }}}
                        />
                      </Grid>
                      <Grid item xs={6}>
                        <TextField 
                          type="time" 
                          label="Start Time" 
                          fullWidth 
                          size="small"
                          value={bookingTime} 
                          onChange={(e) => setBookingTime(e.target.value)}
                          InputLabelProps={{ shrink: true }}
                          variant="filled" 
                          sx={{ '& .MuiFilledInput-root': { borderRadius: '10px', bgcolor: COLORS.cream }}}
                        />
                      </Grid>
                    </Grid>
                  </Box>

                  <FormControl fullWidth variant="filled" size="small">
                    <InputLabel>Type of Care Needed</InputLabel>
                    <Select 
                      value={serviceType} 
                      onChange={(e) => setServiceType(e.target.value)}
                      sx={{ borderRadius: '10px', bgcolor: COLORS.cream }}
                      disableUnderline
                    >
                      <MenuItem value="General Care">General Personal Care</MenuItem>
                      <MenuItem value="Post-Op Recovery">Post-Surgical Support</MenuItem>
                      <MenuItem value="Elderly Assistance">Elderly Companion Care</MenuItem>
                      <MenuItem value="Dementia Support">Specialized Dementia Care</MenuItem>
                    </Select>
                  </FormControl>

                  <Box>
                    <Typography variant="h6" fontWeight={700} sx={{ mb: 1 }}>Notes for Professional</Typography>
                    <TextField 
                      fullWidth 
                      multiline 
                      rows={3} 
                      placeholder="Describe any specific requirements..."
                      value={bookingNotes}
                      onChange={(e) => setBookingNotes(e.target.value)}
                      variant="filled" 
                      size="small"
                      sx={{ '& .MuiFilledInput-root': { borderRadius: '10px', bgcolor: COLORS.cream }}}
                    />
                  </Box>

                  <Box sx={{ p: 1.5, bgcolor: alpha(COLORS.sage, 0.1), borderRadius: '12px', border: `1px dashed ${COLORS.sage}` }}>
                    <Stack direction="row" justifyContent="space-between">
                      <Typography variant="body2" fontWeight={700}>Estimated Total (2 Hours)</Typography>
                      <Typography variant="body2" fontWeight={700}>
                        R{calculateTotalCost(selectedProvider.hourly_rate, 2)}
                      </Typography>
                    </Stack>
                  </Box>
                </Stack>
              </Grid>
            </Grid>

            <DialogActions sx={{ mt: 3, p: 0 }}>
              <Button onClick={() => setSelectedProvider(null)} sx={{ color: COLORS.taupe, fontWeight: 600 }}>Cancel</Button>
              <PremiumButton 
                variant="contained" 
                onClick={handleBooking} 
                disabled={isBooking}
                sx={{ px: 4 }}
              >
                {isBooking ? <CircularProgress size={20} color="inherit" /> : 'Confirm Booking'}
              </PremiumButton>
            </DialogActions>
          </Box>
        )}
      </Dialog>

      {/* GLOBAL FEEDBACK SYSTEM */}
      <Snackbar 
        open={!!successMsg} 
        autoHideDuration={6000} 
        onClose={() => setSuccessMsg(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          severity="success" 
          variant="filled" 
          sx={{ width: '100%', borderRadius: '12px', bgcolor: COLORS.success, px: 3 }}
        >
          <Typography fontWeight={600}>{successMsg}</Typography>
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ClientDashboard;