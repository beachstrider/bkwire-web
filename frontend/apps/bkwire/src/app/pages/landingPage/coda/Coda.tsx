import { useAuth0 } from '@auth0/auth0-react';
import { Button, Typography } from '@mui/material';
import { CodaRoot } from './Coda.styled';

export const Coda = () => {
  const { loginWithRedirect } = useAuth0();
  return (
    <CodaRoot>
      <Typography variant="h1">
        Reliable bankruptcy data is hard to find.
      </Typography>
      <Typography variant="h2">Stop digging now!</Typography>
      <Button
        size="large"
        variant="contained"
        onClick={() => loginWithRedirect({ screen_hint: 'signup' })}
      >
        SIGN UP TODAY
      </Button>
    </CodaRoot>
  );
};
