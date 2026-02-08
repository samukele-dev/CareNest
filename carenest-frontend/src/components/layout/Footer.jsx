import React from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  Link,
  IconButton,
  Divider,
} from '@mui/material';
import {
  Facebook,
  Twitter,
  Instagram,
  LinkedIn,
  Phone,
  Mail,
  LocationOn,
} from '@mui/icons-material';
import styled from 'styled-components';
import { colors } from '../ui/styled';

const FooterContainer = styled(Box)`
  background: ${colors.taupe};
  color: white;
  padding: 60px 0 30px;
`;

const FooterLink = styled(Link)`
  color: ${colors.cream} !important;
  text-decoration: none;
  display: block;
  margin-bottom: 12px;
  transition: color 0.2s ease;

  &:hover {
    color: ${colors.sage} !important;
  }
`;

const Footer = () => {
  return (
    <FooterContainer>
      <Container maxWidth="lg">
        <Grid container spacing={6}>
          <Grid item xs={12} md={4}>
            <Typography variant="h5" sx={{ color: 'white', mb: 3, fontWeight: 700 }}>
              CareNest
            </Typography>
            <Typography variant="body2" sx={{ color: colors.cream, mb: 3 }}>
              Professional caregiving platform connecting families with verified, 
              compassionate caregivers for peace of mind and quality care.
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
              <IconButton sx={{ color: colors.cream, '&:hover': { color: colors.sage } }}>
                <Facebook />
              </IconButton>
              <IconButton sx={{ color: colors.cream, '&:hover': { color: colors.sage } }}>
                <Twitter />
              </IconButton>
              <IconButton sx={{ color: colors.cream, '&:hover': { color: colors.sage } }}>
                <Instagram />
              </IconButton>
              <IconButton sx={{ color: colors.cream, '&:hover': { color: colors.sage } }}>
                <LinkedIn />
              </IconButton>
            </Box>
          </Grid>

          <Grid item xs={6} md={2}>
            <Typography variant="h6" sx={{ color: 'white', mb: 3, fontWeight: 600 }}>
              Company
            </Typography>
            <FooterLink href="/about">About Us</FooterLink>
            <FooterLink href="/careers">Careers</FooterLink>
            <FooterLink href="/blog">Blog</FooterLink>
            <FooterLink href="/press">Press</FooterLink>
          </Grid>

          <Grid item xs={6} md={2}>
            <Typography variant="h6" sx={{ color: 'white', mb: 3, fontWeight: 600 }}>
              Services
            </Typography>
            <FooterLink href="/elderly-care">Elderly Care</FooterLink>
            <FooterLink href="/special-needs">Special Needs</FooterLink>
            <FooterLink href="/post-operative">Post-Operative</FooterLink>
            <FooterLink href="/respite-care">Respite Care</FooterLink>
          </Grid>

          <Grid item xs={12} md={4}>
            <Typography variant="h6" sx={{ color: 'white', mb: 3, fontWeight: 600 }}>
              Contact Us
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Phone sx={{ color: colors.sage, mr: 2 }} />
              <Typography variant="body2" sx={{ color: colors.cream }}>
                (555) 123-4567
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Mail sx={{ color: colors.sage, mr: 2 }} />
              <Typography variant="body2" sx={{ color: colors.cream }}>
                support@carenest.com
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <LocationOn sx={{ color: colors.sage, mr: 2 }} />
              <Typography variant="body2" sx={{ color: colors.cream }}>
                123 Care Street, Suite 100
                <br />
                San Francisco, CA 94107
              </Typography>
            </Box>
          </Grid>
        </Grid>

        <Divider sx={{ my: 6, borderColor: 'rgba(255,255,255,0.1)' }} />

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" sx={{ color: colors.cream }}>
            © {new Date().getFullYear()} CareNest. All rights reserved.
          </Typography>
          <Box sx={{ display: 'flex', gap: 3 }}>
            <Link href="/privacy" sx={{ color: colors.cream, textDecoration: 'none', fontSize: '0.875rem' }}>
              Privacy Policy
            </Link>
            <Link href="/terms" sx={{ color: colors.cream, textDecoration: 'none', fontSize: '0.875rem' }}>
              Terms of Service
            </Link>
            <Link href="/cookies" sx={{ color: colors.cream, textDecoration: 'none', fontSize: '0.875rem' }}>
              Cookie Policy
            </Link>
          </Box>
        </Box>
      </Container>
    </FooterContainer>
  );
};

export default Footer;