import { useAuth0 } from '@auth0/auth0-react';
import { Box, Button, Typography, useTheme } from '@mui/material';
import { useGetSplash } from '../../../api/api.hooks';
import { formatKMB } from '../../../utils/number';
import { HeroRoot } from './Hero.styled';

// const recentUnsecuredCreditors = [
//   {
//     creditor_name: 'Acme Foods Inc',
//     industry: 'Food & staples',
//     unsecured_claim: '$12.2m',
//   },
//   {
//     creditorName: 'Bel Air Logistics Inc',
//     bankruptcyName: 'Transportation',
//     loss: '$11.7m',
//   },
//   {
//     creditorName: 'Kids Space Inc',
//     bankruptcyName: 'Miscellaneous',
//     loss: '$10.5m',
//   },
//   {
//     creditorName: 'Jokers Import Inc',
//     bankruptcyName: 'Retail trade',
//     loss: '$9.5m',
//   },
//   {
//     creditorName: 'Coyote Properties',
//     bankruptcyName: 'Retail trade',
//     loss: '$4.7m',
//   },
// ];

export const Hero = () => {
  const theme = useTheme();
  const { loginWithRedirect } = useAuth0();
  const { data, isLoading } = useGetSplash();

  return (
    <HeroRoot>
      <Box className="hero-caption">
        <Typography variant="h1">Bankruptcy insights for companies</Typography>
        <Typography variant="body1" mt={1} mb={2}>
          Protect your assets and your bottom line with BKwire's personalized,
          targeted, bankruptcy dashboard.
        </Typography>
        <Button
          variant="contained"
          onClick={() => loginWithRedirect({ screen_hint: 'signup' })}
        >
          SIGN UP TODAY
        </Button>
      </Box>
      <Box className="hero-image">
        <Box className="recent-unsecurred-creditors">
          <Typography className="header" variant="body2">
            Recent unsecured creditors
          </Typography>
          {(data && Array.isArray(data) ? data : []).map((ruc) => (
            <Box className="ruc" key={ruc.creditor_name}>
              <Box flexGrow={1}>
                <Typography variant="body1" noWrap width={230}>
                  {ruc.creditor_name}
                </Typography>
                <Typography variant="body3" color={theme.palette.grey[600]}>
                  {ruc.industry || 'Miscellaneous'}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body3" color={theme.palette.grey[600]}>
                  ${formatKMB(ruc.unsecured_claim)}
                </Typography>
              </Box>
            </Box>
          ))}
          <Button
            className="footer"
            variant="contained"
            onClick={() => loginWithRedirect({ screen_hint: 'signup' })}
          >
            SIGN UP TO VIEW ALL
          </Button>
        </Box>
      </Box>
    </HeroRoot>
  );
};
