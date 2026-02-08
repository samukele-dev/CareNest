import React, { useState } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AppBar,
  Toolbar,
  IconButton,
  Button,
  Box,
  Avatar,
  Menu,
  MenuItem,
  Typography,
  Divider,
  Badge,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Home,
  Person,
  MedicalServices,
  Dashboard,
  Notifications,
  Message,
  Settings,
  Logout,
  ArrowForward,
  Close,
} from '@mui/icons-material';
import styled from 'styled-components';
import { useAuth } from '../../contexts/AuthContext';
import { colors } from '../ui/styled';

// Create motion components
const MotionDiv = motion.create('div');
const MotionLink = motion.create(Link);
const MotionButton = motion.create(Button);

// Styled components for navbar
const StyledAppBar = styled(AppBar)`
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid ${colors.peach}30;
  box-shadow: 0 2px 20px rgba(139, 116, 91, 0.05) !important;
  transition: all 0.3s ease;

  &.scrolled {
    box-shadow: 0 4px 30px rgba(139, 116, 91, 0.1) !important;
    background: rgba(255, 255, 255, 0.98) !important;
  }
`;

const LogoContainer = styled(MotionDiv)`
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
`;

const LogoCircle = styled.div`
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, ${colors.sage} 0%, ${colors.peach} 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 18px;
  box-shadow: 0 4px 12px rgba(139, 148, 116, 0.3);
`;

const NavLink = styled(MotionLink)`
  text-decoration: none;
  color: ${colors.taupe};
  font-weight: 500;
  font-size: 15px;
  padding: 8px 16px;
  border-radius: 10px;
  transition: all 0.2s ease;
  position: relative;

  &:hover {
    color: ${colors.sage};
    background: ${colors.sage}10;
  }

  &.active {
    color: ${colors.sage};
    font-weight: 600;

    &::after {
      content: '';
      position: absolute;
      bottom: -8px;
      left: 50%;
      transform: translateX(-50%);
      width: 4px;
      height: 4px;
      background: ${colors.sage};
      border-radius: 50%;
    }
  }
`;

const GetStartedButton = styled(MotionButton)`
  && {
    background: linear-gradient(135deg, ${colors.sage} 0%, #737A5F 100%);
    color: white;
    font-weight: 600;
    padding: 10px 24px;
    border-radius: 10px;
    text-transform: none;
    box-shadow: 0 4px 15px rgba(139, 148, 116, 0.3);
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

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(139, 148, 116, 0.4);

      &::before {
        left: 100%;
      }
    }
  }
`;

const UserMenuContainer = styled(MotionDiv)`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;

  &:hover {
    background: ${colors.cream};
    border-color: ${colors.peach}30;
  }
`;

const NotificationBadge = styled(Badge)`
  && {
    .MuiBadge-badge {
      background: linear-gradient(135deg, ${colors.sage} 0%, #737A5F 100%);
      color: white;
      font-size: 10px;
      font-weight: bold;
      border: 2px solid white;
    }
  }
`;

const MobileDrawer = styled(Drawer)`
  .MuiDrawer-paper {
    width: 280px;
    background: ${colors.cream};
    border-right: 1px solid ${colors.peach}30;
    backdrop-filter: blur(10px);
  }
`;

const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState(null);
  const [notificationsAnchor, setNotificationsAnchor] = useState(null);

  // Handle scroll effect
  React.useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navItems = [
    { label: 'Home', path: '/', icon: <Home /> },
    { label: 'Features', path: '/#features', icon: <MedicalServices /> },
    { label: 'How It Works', path: '/#how-it-works', icon: <Dashboard /> },
    { label: 'Testimonials', path: '/#testimonials', icon: <Person /> },
    { label: 'Contact', path: '/#contact', icon: <Message /> },
  ];

  const handleGetStarted = () => {
    if (isAuthenticated) {
      // Redirect based on user type
      switch (user?.type) {
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
    } else {
      navigate('/login');
    }
  };

  const handleUserMenuOpen = (event) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const handleLogout = async () => {
    handleUserMenuClose();
    await logout();
    navigate('/');
  };

  const handleMobileDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleNotificationsOpen = (event) => {
    setNotificationsAnchor(event.currentTarget);
  };

  const handleNotificationsClose = () => {
    setNotificationsAnchor(null);
  };

  const drawerContent = (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <LogoContainer onClick={() => navigate('/')}>
          
          <Typography variant="h6" sx={{ color: colors.taupe, fontWeight: 700 }}>
            CareNest
          </Typography>
        </LogoContainer>
        <IconButton onClick={handleMobileDrawerToggle}>
          <Close sx={{ color: colors.taupe }} />
        </IconButton>
      </Box>

      <Divider sx={{ mb: 3 }} />

      <List>
        {navItems.map((item) => (
          <ListItem
            key={item.label}
            component={Link}
            to={item.path}
            onClick={handleMobileDrawerToggle}
            sx={{
              borderRadius: 2,
              mb: 1,
              color: location.pathname === item.path ? colors.sage : colors.taupe,
              bgcolor: location.pathname === item.path ? `${colors.sage}10` : 'transparent',
              '&:hover': {
                bgcolor: `${colors.sage}10`,
              },
            }}
          >
            <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItem>
        ))}
      </List>

      {isAuthenticated ? (
        <>
          <Divider sx={{ my: 2 }} />
          <List>
            <ListItem
              component={Link}
              to={`/dashboard/${user?.type}`}
              onClick={handleMobileDrawerToggle}
              sx={{
                borderRadius: 2,
                mb: 1,
                color: colors.sage,
                bgcolor: `${colors.sage}10`,
              }}
            >
              <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>
                <Dashboard />
              </ListItemIcon>
              <ListItemText primary="Dashboard" />
            </ListItem>
            <ListItem
              component={Link}
              to="/profile"
              onClick={handleMobileDrawerToggle}
              sx={{
                borderRadius: 2,
                mb: 1,
                color: colors.taupe,
                '&:hover': { bgcolor: `${colors.sage}10` },
              }}
            >
              <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>
                <Person />
              </ListItemIcon>
              <ListItemText primary="Profile" />
            </ListItem>
            <ListItem
              onClick={handleLogout}
              sx={{
                borderRadius: 2,
                color: colors.brown,
                '&:hover': { bgcolor: `${colors.peach}20` },
              }}
            >
              <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>
                <Logout />
              </ListItemIcon>
              <ListItemText primary="Logout" />
            </ListItem>
          </List>
        </>
      ) : (
        <Box sx={{ mt: 3, p: 2 }}>
          <GetStartedButton
            fullWidth
            onClick={() => {
              handleMobileDrawerToggle();
              handleGetStarted();
            }}
            endIcon={<ArrowForward />}
          >
            Get Started
          </GetStartedButton>
        </Box>
      )}
    </Box>
  );

  return (
    <>
      <StyledAppBar position="fixed" className={scrolled ? 'scrolled' : ''}>
        <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 2, md: 4 } }}>
          {/* Left: Logo */}
          <LogoContainer 
            onClick={() => navigate('/')} 
            whileTap={{ scale: 0.95 }}
          >
            <LogoCircle>CN</LogoCircle>
            <Typography
              variant="h6"
              sx={{
                color: colors.taupe,
                fontWeight: 700,
                display: { xs: 'none', md: 'block' },
              }}
            >
              CareNest
            </Typography>
          </LogoContainer>

          {/* Center: Desktop Navigation */}
          <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 1 }}>
            {navItems.map((item) => (
              <NavLink
                key={item.label}
                to={item.path}
                className={location.pathname === item.path ? 'active' : ''}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {item.label}
              </NavLink>
            ))}
          </Box>

          {/* Right: Actions */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {isAuthenticated ? (
              <>
                {/* Notifications */}
                <IconButton
                  onClick={handleNotificationsOpen}
                  sx={{ color: colors.taupe }}
                >
                  <NotificationBadge badgeContent={3} color="primary">
                    <Notifications />
                  </NotificationBadge>
                </IconButton>

                {/* User Menu */}
                <UserMenuContainer
                  onClick={handleUserMenuOpen}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Avatar
                    sx={{
                      width: 36,
                      height: 36,
                      bgcolor: colors.sage,
                      fontSize: 14,
                    }}
                    src={user?.avatar}
                  >
                    {user?.name?.charAt(0) || 'U'}
                  </Avatar>
                  <Box sx={{ display: { xs: 'none', lg: 'block' } }}>
                    <Typography variant="body2" sx={{ color: colors.taupe, fontWeight: 600 }}>
                      {user?.name || 'User'}
                    </Typography>
                    <Typography variant="caption" sx={{ color: colors.brown }}>
                      {user?.type?.toUpperCase() || 'USER'}
                    </Typography>
                  </Box>
                </UserMenuContainer>
              </>
            ) : (
              <>
                <Button
                  component={Link}
                  to="/login"
                  sx={{
                    color: colors.sage,
                    fontWeight: 500,
                    display: { xs: 'none', sm: 'block' },
                  }}
                >
                  Sign In
                </Button>
                <GetStartedButton
                  onClick={handleGetStarted}
                  endIcon={<ArrowForward />}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Get Started
                </GetStartedButton>
              </>
            )}

            {/* Mobile Menu Button */}
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="end"
              onClick={handleMobileDrawerToggle}
              sx={{ display: { md: 'none' }, color: colors.taupe }}
            >
              <MenuIcon />
            </IconButton>
          </Box>
        </Toolbar>
      </StyledAppBar>

      {/* Mobile Drawer */}
      <MobileDrawer
        anchor="right"
        open={mobileOpen}
        onClose={handleMobileDrawerToggle}
        ModalProps={{ keepMounted: true }}
      >
        {drawerContent}
      </MobileDrawer>

      {/* User Menu Dropdown */}
      <Menu
        anchorEl={userMenuAnchor}
        open={Boolean(userMenuAnchor)}
        onClose={handleUserMenuClose}
        PaperProps={{
          sx: {
            mt: 1.5,
            minWidth: 200,
            borderRadius: 2,
            boxShadow: '0 10px 40px rgba(139, 116, 91, 0.15)',
            border: `1px solid ${colors.peach}30`,
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="subtitle2" sx={{ color: colors.taupe, fontWeight: 600 }}>
            {user?.name || 'User'}
          </Typography>
          <Typography variant="caption" sx={{ color: colors.brown }}>
            {user?.email || 'user@example.com'}
          </Typography>
        </Box>
        <Divider />
        <MenuItem
          component={Link}
          to={`/dashboard/${user?.type}`}
          onClick={handleUserMenuClose}
          sx={{ color: colors.taupe }}
        >
          <Dashboard sx={{ mr: 2, fontSize: 20 }} />
          Dashboard
        </MenuItem>
        <MenuItem
          component={Link}
          to="/profile"
          onClick={handleUserMenuClose}
          sx={{ color: colors.taupe }}
        >
          <Person sx={{ mr: 2, fontSize: 20 }} />
          Profile
        </MenuItem>
        <MenuItem
          component={Link}
          to="/settings"
          onClick={handleUserMenuClose}
          sx={{ color: colors.taupe }}
        >
          <Settings sx={{ mr: 2, fontSize: 20 }} />
          Settings
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout} sx={{ color: colors.brown }}>
          <Logout sx={{ mr: 2, fontSize: 20 }} />
          Logout
        </MenuItem>
      </Menu>

      {/* Notifications Menu */}
      <Menu
        anchorEl={notificationsAnchor}
        open={Boolean(notificationsAnchor)}
        onClose={handleNotificationsClose}
        PaperProps={{
          sx: {
            mt: 1.5,
            width: 320,
            borderRadius: 2,
            boxShadow: '0 10px 40px rgba(139, 116, 91, 0.15)',
            border: `1px solid ${colors.peach}30`,
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="subtitle1" sx={{ color: colors.taupe, fontWeight: 600 }}>
            Notifications
          </Typography>
        </Box>
        <Divider />
        <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
          {[
            { id: 1, title: 'New message', time: '2 min ago', unread: true },
            { id: 2, title: 'Appointment reminder', time: '1 hour ago', unread: true },
            { id: 3, title: 'Profile updated', time: '2 hours ago', unread: false },
          ].map((notification) => (
            <MenuItem
              key={notification.id}
              sx={{
                bgcolor: notification.unread ? `${colors.sage}10` : 'transparent',
                borderLeft: notification.unread ? `3px solid ${colors.sage}` : 'none',
              }}
            >
              <Box sx={{ flex: 1 }}>
                <Typography variant="body2" sx={{ color: colors.taupe }}>
                  {notification.title}
                </Typography>
                <Typography variant="caption" sx={{ color: colors.brown }}>
                  {notification.time}
                </Typography>
              </Box>
            </MenuItem>
          ))}
        </Box>
        <Divider />
        <MenuItem
          component={Link}
          to="/notifications"
          onClick={handleNotificationsClose}
          sx={{ justifyContent: 'center', color: colors.sage }}
        >
          View All Notifications
        </MenuItem>
      </Menu>

      {/* Spacer for fixed navbar */}
      <Toolbar />
    </>
  );
};

export default Navbar;