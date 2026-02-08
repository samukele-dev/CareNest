/**
 * CareNest - Modern Childcare Matching Platform
 * Simple, beautiful, and trustworthy childcare solutions
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Avatar,
  Chip,
  IconButton,
  Paper,
  Stack,
  useTheme,
  useMediaQuery,
  alpha,
  Divider,
  AppBar,
  Toolbar,
  Drawer,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import {
  ArrowForward,
  CheckCircle,
  Star,
  PlayCircle,
  Security,
  People,
  ChildCare,
  VerifiedUser,
  FamilyRestroom,
  Schedule,
  Login,
  Menu as MenuIcon,
  Close as CloseIcon,
  WavingHand,
  Favorite,
  ThumbUp,
  EmojiEmotions,
  Diversity3,
  Handshake
} from '@mui/icons-material';
import { motion } from 'framer-motion';

// Define your colors
const colors = {
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

const LandingPage = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [animatedText, setAnimatedText] = useState('');
  const fullText = 'Childcare Match';

  // Text typing animation
  useEffect(() => {
    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex <= fullText.length) {
        setAnimatedText(fullText.slice(0, currentIndex));
        currentIndex++;
      } else {
        clearInterval(interval);
      }
    }, 100);

    return () => clearInterval(interval);
  }, []);

  // Animation variants
  const fadeInUp = {
    hidden: { opacity: 0, y: 60 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { 
        duration: 0.8,
        ease: "easeOut"
      }
    }
  };

  // Data arrays
  const features = [
    {
      icon: <VerifiedUser sx={{ fontSize: 48, color: colors.sage }} />,
      title: 'Smart Matching',
      description: 'Find caregivers who truly understand your family\'s unique needs and preferences.',
      stat: '98% Match Rate',
      color: colors.sage
    },
    {
      icon: <Security sx={{ fontSize: 48, color: colors.success }} />,
      title: 'Vetted & Verified',
      description: 'Every caregiver undergoes comprehensive background checks and verification.',
      stat: '100% Verified',
      color: colors.success
    },
    {
      icon: <Schedule sx={{ fontSize: 48, color: colors.taupe }} />,
      title: 'Flexible Scheduling',
      description: 'Find care that fits your family\'s unique routine and schedule.',
      stat: '24/7 Available',
      color: colors.taupe
    },
    {
      icon: <People sx={{ fontSize: 48, color: colors.peach }} />,
      title: 'Community Support',
      description: 'Join a community of parents with support and exclusive resources.',
      stat: '2,500+ Families',
      color: colors.peach
    }
  ];

  const testimonials = [
    {
      name: 'Sarah M.',
      role: 'Mother of two',
      content: 'Found the perfect nanny in 48 hours. The process was seamless and the match is perfect!',
      rating: 5,
      avatar: 'SM'
    },
    {
      name: 'Michael T.',
      role: 'Single parent',
      content: 'As a working single parent, the flexibility and quality of caregivers has been life-changing.',
      rating: 5,
      avatar: 'MT'
    },
    {
      name: 'The Johnson Family',
      role: 'Family of four',
      content: 'The community aspect and ongoing support make CareNest stand out from other services.',
      rating: 5,
      avatar: 'JF'
    }
  ];

  return (
    <Box sx={{ 
      bgcolor: colors.cream, 
      minHeight: '100vh',
      overflowX: 'hidden'
    }}>
      
      {/* Navigation */}
      <AppBar 
        position="fixed" 
        sx={{
          bgcolor: 'rgba(253, 251, 247, 0.95)',
          backdropFilter: 'blur(20px)',
          boxShadow: '0 4px 30px rgba(0, 0, 0, 0.05)',
          borderBottom: `1px solid ${colors.border}`
        }}
      >
        <Container maxWidth="xl">
          <Toolbar disableGutters sx={{ justifyContent: 'space-between', py: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <motion.div
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.5 }}
              >
                <ChildCare sx={{ fontSize: 32, color: colors.sage }} />
              </motion.div>
              <Typography variant="h5" fontWeight={900} color={colors.taupe}>
                CareNest
              </Typography>
            </Box>

            {/* Desktop Navigation */}
            <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 4, alignItems: 'center' }}>
              {['How it Works', 'Features', 'Testimonials', 'Pricing'].map((item) => (
                <Typography 
                  key={item}
                  sx={{ 
                    color: colors.taupe,
                    fontWeight: 600,
                    cursor: 'pointer',
                    '&:hover': { color: colors.sage }
                  }}
                >
                  {item}
                </Typography>
              ))}
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Button
                variant="outlined"
                startIcon={<Login />}
                onClick={() => navigate('/login')}
                sx={{
                  borderColor: colors.sage,
                  color: colors.sage,
                  fontWeight: 600,
                  borderRadius: '12px',
                  px: 3,
                  '&:hover': {
                    borderColor: colors.sage,
                    bgcolor: alpha(colors.sage, 0.05)
                  }
                }}
              >
                Log In
              </Button>
              <Button 
                variant="contained"
                onClick={() => navigate('/signup')}
                sx={{
                  bgcolor: colors.sage,
                  color: colors.white,
                  fontWeight: 700,
                  borderRadius: '12px',
                  px: 3,
                  '&:hover': {
                    bgcolor: colors.taupe,
                    transform: 'translateY(-2px)'
                  }
                }}
              >
                Get Started
              </Button>
              <IconButton 
                sx={{ display: { xs: 'flex', md: 'none' }, color: colors.taupe }}
                onClick={() => setMobileMenuOpen(true)}
              >
                <MenuIcon />
              </IconButton>
            </Box>
          </Toolbar>
        </Container>
      </AppBar>

      {/* Mobile Menu Drawer */}
      <Drawer
        anchor="right"
        open={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
        PaperProps={{ sx: { width: '80%', bgcolor: colors.cream, p: 3 } }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 4 }}>
          <IconButton onClick={() => setMobileMenuOpen(false)}>
            <CloseIcon />
          </IconButton>
        </Box>
        <List>
          {['How it Works', 'Features', 'Testimonials', 'Pricing', 'Log In', 'Get Started'].map((item) => (
            <ListItem 
              button 
              key={item}
              onClick={() => {
                setMobileMenuOpen(false);
                if (item === 'Log In') navigate('/login');
                if (item === 'Get Started') navigate('/signup');
              }}
              sx={{ mb: 2 }}
            >
              <ListItemText 
                primary={item} 
                primaryTypographyProps={{ variant: 'h5', fontWeight: 800, color: colors.taupe }} 
              />
            </ListItem>
          ))}
        </List>
      </Drawer>

      {/* Hero Section */}
      <Box sx={{ pt: 20, pb: 15, position: 'relative' }}>
        <Container maxWidth="xl">
          <Grid container spacing={8} alignItems="center">
            <Grid item xs={12} lg={6}>
              <motion.div
                initial="hidden"
                animate="visible"
                variants={{
                  hidden: { opacity: 0 },
                  visible: {
                    opacity: 1,
                    transition: {
                      staggerChildren: 0.2
                    }
                  }
                }}
              >
                <motion.div variants={fadeInUp}>
                  <Chip
                    label="Modern Childcare Matching"
                    sx={{
                      bgcolor: alpha(colors.sage, 0.1),
                      color: colors.sage,
                      fontWeight: 700,
                      mb: 4,
                      px: 2,
                      py: 1
                    }}
                    icon={<FamilyRestroom />}
                  />
                </motion.div>

                <motion.div variants={fadeInUp}>
                  <Typography
                    variant="h1"
                    sx={{
                      fontSize: { xs: '3rem', md: '4.5rem', lg: '5.5rem' },
                      fontWeight: 900,
                      lineHeight: 1.1,
                      color: colors.taupe,
                      mb: 3,
                    }}
                  >
                    Find Your Perfect
                    <Box component="span" sx={{
                      display: 'block',
                      position: 'relative'
                    }}>
                      <Box
                        sx={{
                          background: `linear-gradient(135deg, ${colors.sage} 0%, ${colors.peach} 100%)`,
                          WebkitBackgroundClip: 'text',
                          WebkitTextFillColor: 'transparent',
                          backgroundClip: 'text',
                          display: 'inline-block'
                        }}
                      >
                        {animatedText}
                        <Box 
                          component="span" 
                          sx={{ 
                            display: 'inline-block',
                            width: '3px',
                            height: '1em',
                            bgcolor: colors.sage,
                            ml: 0.5,
                            animation: 'blink 1s infinite'
                          }} 
                        />
                      </Box>
                    </Box>
                  </Typography>
                </motion.div>

                <motion.div variants={fadeInUp}>
                  <Typography
                    variant="h5"
                    sx={{
                      color: colors.brown,
                      mb: 5,
                      fontWeight: 400,
                      opacity: 0.9,
                      maxWidth: '90%',
                    }}
                  >
                    Connect with trusted, verified caregivers who share your values and understand your family's unique needs.
                    <br />
                    <Box
                      component="span"
                      sx={{ fontWeight: 600, color: colors.sage }}
                    >
                      Simple, safe, and stress-free.
                    </Box>
                  </Typography>
                </motion.div>

                <motion.div variants={fadeInUp}>
                  <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                      <Button
                        variant="contained"
                        onClick={() => navigate('/signup')}
                        endIcon={<ArrowForward />}
                        sx={{
                          bgcolor: colors.sage,
                          color: colors.white,
                          fontWeight: 700,
                          px: 4,
                          py: 2,
                          borderRadius: '16px',
                          fontSize: '1.1rem',
                          '&:hover': {
                            bgcolor: colors.taupe,
                            transform: 'translateY(-2px)'
                          }
                        }}
                      >
                        Find Your Match
                      </Button>
                    </motion.div>
                    
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                      <Button
                        variant="outlined"
                        startIcon={<PlayCircle />}
                        sx={{
                          borderColor: colors.sage,
                          color: colors.sage,
                          fontWeight: 600,
                          px: 4,
                          py: 2,
                          borderRadius: '16px',
                          '&:hover': {
                            borderColor: colors.sage,
                            bgcolor: alpha(colors.sage, 0.05)
                          }
                        }}
                      >
                        Watch Demo
                      </Button>
                    </motion.div>
                  </Stack>
                </motion.div>

                {/* Stats */}
                <motion.div variants={fadeInUp}>
                  <Stack direction="row" spacing={4} sx={{ mt: 8, flexWrap: 'wrap' }}>
                    {[
                      { value: '2,500+', label: 'Happy Families', icon: <Diversity3 /> },
                      { value: '98%', label: 'Match Rate', icon: <Favorite /> },
                      { value: '24/7', label: 'Support', icon: <Handshake /> }
                    ].map((stat, idx) => (
                      <motion.div
                        key={idx}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <Box sx={{ textAlign: 'center' }}>
                          <Box sx={{ color: colors.sage, fontSize: 32, mb: 1 }}>
                            {stat.icon}
                          </Box>
                          <Typography variant="h4" fontWeight={900} color={colors.sage}>
                            {stat.value}
                          </Typography>
                          <Typography variant="body2" color={colors.brown}>
                            {stat.label}
                          </Typography>
                        </Box>
                      </motion.div>
                    ))}
                  </Stack>
                </motion.div>
              </motion.div>
            </Grid>

            <Grid item xs={12} lg={6}>
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.8, delay: 0.3 }}
              >
                {/* Simple image gallery without external URLs */}
                <Box sx={{ position: 'relative', height: 500 }}>
                  {/* Main Card */}
                  <Paper
                    elevation={8}
                    sx={{
                      width: 300,
                      height: 400,
                      borderRadius: '24px',
                      overflow: 'hidden',
                      position: 'absolute',
                      top: 0,
                      right: '10%',
                      zIndex: 3,
                      border: `4px solid ${colors.white}`,
                      background: `linear-gradient(135deg, ${colors.peach}, ${colors.sage})`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <Box sx={{ textAlign: 'center', p: 4 }}>
                      <ChildCare sx={{ fontSize: 80, color: colors.white, mb: 2 }} />
                      <Typography variant="h5" color="white" fontWeight={700}>
                        Happy Kids &<br />
                        Trusted Caregivers
                      </Typography>
                    </Box>
                  </Paper>

                  {/* Top Left Card */}
                  <Paper
                    elevation={6}
                    sx={{
                      width: 180,
                      height: 240,
                      borderRadius: '20px',
                      position: 'absolute',
                      top: '10%',
                      left: 0,
                      zIndex: 2,
                      transform: 'rotate(-5deg)',
                      border: `3px solid ${colors.white}`,
                      background: colors.sage,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <Box sx={{ textAlign: 'center', p: 3 }}>
                      <People sx={{ fontSize: 48, color: colors.white, mb: 2 }} />
                      <Typography variant="body1" color="white" fontWeight={600}>
                        Professional<br />Nannies
                      </Typography>
                    </Box>
                  </Paper>

                  {/* Bottom Right Card */}
                  <Paper
                    elevation={6}
                    sx={{
                      width: 200,
                      height: 260,
                      borderRadius: '20px',
                      position: 'absolute',
                      bottom: 0,
                      right: 0,
                      zIndex: 2,
                      transform: 'rotate(3deg)',
                      border: `3px solid ${colors.white}`,
                      background: colors.peach,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <Box sx={{ textAlign: 'center', p: 3 }}>
                      <Favorite sx={{ fontSize: 48, color: colors.taupe, mb: 2 }} />
                      <Typography variant="body1" color={colors.taupe} fontWeight={600}>
                        Loving<br />Environment
                      </Typography>
                    </Box>
                  </Paper>

                  {/* Floating Badges */}
                  <Paper
                    sx={{
                      p: 2,
                      borderRadius: '16px',
                      background: `linear-gradient(135deg, ${colors.sage}, ${colors.taupe})`,
                      color: 'white',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1,
                      position: 'absolute',
                      top: '40%',
                      left: '5%',
                      zIndex: 4,
                      boxShadow: `0 10px 30px ${alpha(colors.sage, 0.3)}`
                    }}
                  >
                    <ThumbUp sx={{ fontSize: 20 }} />
                    <Typography variant="caption" fontWeight={700}>
                      96% Match Rate
                    </Typography>
                  </Paper>

                  <Paper
                    sx={{
                      p: 2,
                      borderRadius: '16px',
                      background: colors.peach,
                      color: colors.taupe,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1,
                      position: 'absolute',
                      bottom: '30%',
                      left: '15%',
                      zIndex: 4,
                      boxShadow: `0 10px 30px ${alpha(colors.peach, 0.3)}`
                    }}
                  >
                    <EmojiEmotions sx={{ fontSize: 20 }} />
                    <Typography variant="caption" fontWeight={700}>
                      Happy Kids
                    </Typography>
                  </Paper>
                </Box>
              </motion.div>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Features Section */}
      <Box sx={{ py: 15, bgcolor: colors.white }}>
        <Container maxWidth="xl">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={{
              hidden: { opacity: 0 },
              visible: {
                opacity: 1,
                transition: {
                  staggerChildren: 0.2
                }
              }
            }}
          >
            <motion.div variants={fadeInUp} sx={{ textAlign: 'center', mb: 10 }}>
              <Typography
                variant="h2"
                sx={{
                  fontSize: { xs: '2.5rem', md: '3.5rem' },
                  fontWeight: 900,
                  color: colors.taupe,
                  mb: 3,
                }}
              >
                Why Families Love
                <Box component="span" sx={{
                  display: 'block',
                  color: colors.sage
                }}>
                  CareNest
                </Box>
              </Typography>
              <Typography variant="h6" color={colors.brown} sx={{ maxWidth: 700, mx: 'auto' }}>
                We've simplified childcare matching with a focus on quality, safety, and compatibility
              </Typography>
            </motion.div>

            <Grid container spacing={4}>
              {features.map((feature, index) => (
                <Grid item xs={12} sm={6} md={3} key={index}>
                  <motion.div
                    variants={{
                      hidden: { opacity: 0, scale: 0.8 },
                      visible: {
                        opacity: 1,
                        scale: 1,
                        transition: {
                          duration: 0.6
                        }
                      }
                    }}
                    whileInView="visible"
                    viewport={{ once: true }}
                  >
                    <motion.div whileHover={{ y: -10 }}>
                      <Card
                        sx={{
                          height: '100%',
                          borderRadius: '24px',
                          background: colors.white,
                          border: `1px solid ${alpha(feature.color, 0.2)}`,
                          overflow: 'hidden',
                          position: 'relative'
                        }}
                      >
                        <CardContent sx={{ p: 4, textAlign: 'center' }}>
                          <motion.div
                            whileHover={{ rotate: 360 }}
                            transition={{ duration: 0.5 }}
                          >
                            <Box sx={{ 
                              width: 80,
                              height: 80,
                              borderRadius: '20px',
                              bgcolor: alpha(feature.color, 0.1),
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              mb: 3,
                              mx: 'auto'
                            }}>
                              {feature.icon}
                            </Box>
                          </motion.div>
                          
                          <Typography variant="h5" fontWeight={800} color={colors.taupe} mb={2}>
                            {feature.title}
                          </Typography>
                          
                          <Typography variant="body1" color={colors.brown} mb={3}>
                            {feature.description}
                          </Typography>
                          
                          <motion.div whileHover={{ scale: 1.1 }}>
                            <Chip
                              label={feature.stat}
                              sx={{
                                bgcolor: alpha(feature.color, 0.1),
                                color: feature.color,
                                fontWeight: 700,
                                border: `1px solid ${alpha(feature.color, 0.2)}`
                              }}
                            />
                          </motion.div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </motion.div>
        </Container>
      </Box>

      {/* CTA Section */}
      <Box sx={{ 
        py: 20,
        background: `linear-gradient(135deg, ${colors.sage} 0%, ${colors.taupe} 100%)`,
        position: 'relative'
      }}>
        <Container maxWidth="md">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            sx={{ textAlign: 'center' }}
          >
            <motion.div
              animate={{
                y: [0, -20, 0],
              }}
              transition={{
                duration: 4,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              style={{ marginBottom: 40 }}
            >
              <WavingHand sx={{ fontSize: 80, color: 'white' }} />
            </motion.div>
            
            <Typography
              variant="h2"
              sx={{
                color: 'white',
                fontWeight: 900,
                mb: 3,
                fontSize: { xs: '2.5rem', md: '3.5rem' },
              }}
            >
              Ready to Find Your Perfect
              <br />
              Childcare Match?
            </Typography>
            
            <Typography variant="h5" sx={{ 
              color: 'rgba(255, 255, 255, 0.95)', 
              mb: 6,
              maxWidth: 700,
              mx: 'auto',
              lineHeight: 1.6 
            }}>
              Join thousands of families who trust CareNest with their childcare needs.
              Start your journey today.
            </Typography>
            
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={3}
              sx={{ maxWidth: 600, mx: 'auto', mb: 8 }}
            >
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button
                  variant="contained"
                  onClick={() => navigate('/signup')}
                  sx={{
                    bgcolor: 'white',
                    color: colors.sage,
                    fontWeight: 700,
                    px: 5,
                    py: 2,
                    borderRadius: '16px',
                    fontSize: '1.1rem',
                    minWidth: 200,
                    '&:hover': {
                      bgcolor: alpha(colors.white, 0.9)
                    }
                  }}
                >
                  Get Started Free
                </Button>
              </motion.div>

              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button
                  variant="outlined"
                  startIcon={<Login />}
                  onClick={() => navigate('/login')}
                  sx={{
                    borderColor: 'white',
                    color: 'white',
                    fontWeight: 600,
                    px: 4,
                    py: 2,
                    borderRadius: '16px',
                    fontSize: '1.1rem',
                    '&:hover': {
                      borderColor: 'white',
                      bgcolor: alpha(colors.white, 0.1)
                    }
                  }}
                >
                  Log In
                </Button>
              </motion.div>
            </Stack>
            
            <Stack direction="row" spacing={4} justifyContent="center" flexWrap="wrap">
              {['No credit card required', '7-day free trial', 'Cancel anytime'].map((text, index) => (
                <motion.div
                  key={index}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.9)' }} display="flex" alignItems="center">
                    <CheckCircle sx={{ color: colors.peach, mr: 1, fontSize: 16 }} />
                    {text}
                  </Typography>
                </motion.div>
              ))}
            </Stack>
          </motion.div>
        </Container>
      </Box>

      {/* Footer */}
      <Box sx={{ bgcolor: colors.charcoal, color: 'white', py: 8 }}>
        <Container maxWidth="xl">
          <Grid container spacing={6}>
            <Grid item xs={12} md={4}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <ChildCare sx={{ fontSize: 32, color: colors.sage }} />
                <Typography variant="h5" fontWeight={900}>
                  CareNest
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 3, maxWidth: 300 }}>
                Modern childcare matching platform connecting families with trusted caregivers.
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={8}>
              <Grid container spacing={4}>
                {[
                  { title: 'Platform', items: ['How it Works', 'Features', 'Pricing', 'Safety'] },
                  { title: 'Company', items: ['About', 'Careers', 'Press', 'Blog'] },
                  { title: 'Support', items: ['Help Center', 'Contact', 'Community', 'Guides'] },
                  { title: 'Legal', items: ['Privacy', 'Terms', 'Security', 'Cookies'] }
                ].map((section, idx) => (
                  <Grid item xs={6} sm={3} key={idx}>
                    <Typography variant="h6" fontWeight={700} gutterBottom>
                      {section.title}
                    </Typography>
                    <Stack spacing={1}>
                      {section.items.map((item) => (
                        <Typography 
                          key={item} 
                          variant="body2" 
                          sx={{ 
                            color: 'rgba(255, 255, 255, 0.7)', 
                            '&:hover': { color: 'white', cursor: 'pointer' } 
                          }}
                        >
                          {item}
                        </Typography>
                      ))}
                    </Stack>
                  </Grid>
                ))}
              </Grid>
            </Grid>
          </Grid>
          
          <Divider sx={{ my: 6, borderColor: 'rgba(255, 255, 255, 0.1)' }} />
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              © 2024 CareNest. All rights reserved.
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              Made with ❤️ for families everywhere
            </Typography>
          </Box>
        </Container>
      </Box>

      {/* Add CSS animations */}
      <style>{`
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0; }
        }
        
        .typing-cursor {
          display: inline-block;
          width: 3px;
          height: 1em;
          background-color: ${colors.sage};
          margin-left: 2px;
          animation: blink 1s infinite;
        }
      `}</style>
    </Box>
  );
};

export default LandingPage;