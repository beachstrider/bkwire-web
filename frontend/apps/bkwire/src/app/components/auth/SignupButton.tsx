import { useAuth0 } from '@auth0/auth0-react';
import { Button } from '@mui/material';

export const SignupButton = () => {
  const { loginWithRedirect } = useAuth0();
  return (
    <Button
      variant="contained"
      color="primary"
      sx={{ ml: 1, mr: 1 }}
      onClick={() => loginWithRedirect({ screen_hint: 'signup' })}
    >
      TRY FOR FREE
    </Button>
  );
};
