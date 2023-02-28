import React from 'react';
import { Box, IconButton, Typography } from '@mui/material';
import { InfoBox } from './View';
import { ContactCard } from './View.styled';
import { ContactPageOutlined, MoreVert } from '@mui/icons-material';

export const Contacts: React.VFC = () => {
  return (
    <InfoBox
      gridRow="7 / span 2"
      gridColumn="1 / span 4"
      title={'Contact information'}
      icon={<ContactPageOutlined />}
    >
      <Box display="flex" height="100%">
        <ContactCard>
          <Box className="contact-card-header">
            <Typography variant="h2">Debtor</Typography>
            <IconButton>
              <MoreVert />
            </IconButton>
          </Box>
          <Box className="contact-card-content">
            <Typography variant="body2">Acme Foods</Typography>
            <Typography variant="body2">146 SUTER PLACE</Typography>
            <Typography variant="body2">Los Angeles, CA 90019</Typography>
            <Typography variant="body2">United States</Typography>
            <Typography variant="body2">(213) 555-1212</Typography>
          </Box>
        </ContactCard>
        <ContactCard>
          <Box className="contact-card-header">
            <Typography variant="h2">Trustee</Typography>
            <IconButton>
              <MoreVert />
            </IconButton>
          </Box>
          <Box className="contact-card-content">
            <Typography variant="body2">UNITED STATES TRUSTEE (SV)</Typography>
            <Typography variant="body2">
              915 WILSHIRE BLVD, SUITE 1850
            </Typography>
            <Typography variant="body2">Los Angeles, CA 90017</Typography>
            <Typography variant="body2">United States</Typography>
            <Typography variant="body2">(213) 555-1212</Typography>
          </Box>
        </ContactCard>
        <ContactCard>
          <Box className="contact-card-header">
            <Typography variant="h2">Attorney</Typography>
            <IconButton>
              <MoreVert />
            </IconButton>
          </Box>
          <Box className="contact-card-content">
            <Typography variant="body2">Peter C. Bronstein</Typography>
            <Typography variant="body2">
              1901 AVENUE OF THE STARS, 11TH FLR
            </Typography>
            <Typography variant="body2">Los Angeles, CA 90067</Typography>
            <Typography variant="body2">United States</Typography>
            <Typography variant="body2">(310) 555-1212</Typography>
            <Typography variant="body2" color={(t) => t.palette.link.main}>
              pwterbronz@yahoo.com
            </Typography>
          </Box>
        </ContactCard>
        <ContactCard>
          <Box className="contact-card-header">
            <Typography variant="h2">Judge</Typography>
            <IconButton>
              <MoreVert />
            </IconButton>
          </Box>
          <Box className="contact-card-content">
            <Typography variant="body2">Victoria S. Kauffman</Typography>
            <Typography variant="body2">
              1901 AVENUE OF THE STARS, 11TH FLR
            </Typography>
            <Typography variant="body2">Los Angeles, CA 90067</Typography>
            <Typography variant="body2">United States</Typography>
            <Typography variant="body2">(310) 555-1212</Typography>
            <Typography variant="body2" color={(t) => t.palette.link.main}>
              vickys@gmail.com
            </Typography>
          </Box>
        </ContactCard>
      </Box>
    </InfoBox>
  );
};
