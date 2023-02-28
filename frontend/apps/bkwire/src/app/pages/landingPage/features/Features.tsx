import { Box, Typography } from '@mui/material';
import featureFollow from '../../../../assets/feature-follow.png';
import featureGetNotified from '../../../../assets/feature-get-notified.png';
import featureProtectBusiness from '../../../../assets/feature-protect-your-business.png';
import { Feature, FeaturesRoot } from './Features.styled';

const features = [
  {
    title: 'The one source you need to protect your business',
    subtitle:
      'Three lines of copy that describe the value of a key app feature. Make it action-oriented and simple.',
    image: featureProtectBusiness,
  },
  {
    title: 'Get notified about important bankruptcies',
    subtitle:
      'Three lines of copy that describe the value of a key app feature. Make it action-oriented and simple.',
    image: featureGetNotified,
  },
  {
    title: 'Follow any at-risk company and avoid the panic',
    subtitle:
      'Three lines of copy that describe the value of a key app feature. Make it action-oriented and simple.',
    image: featureFollow,
  },
];

export const Features = () => {
  return (
    <FeaturesRoot id="features">
      {features.map((a) => (
        <Feature key={a.title} imgSrc={a.image}>
          <Box className="text">
            <Typography variant="h1">{a.title}</Typography>
            <Typography variant="body1">{a.subtitle}</Typography>
          </Box>
          <Box className="image"></Box>
        </Feature>
      ))}
    </FeaturesRoot>
  );
};
