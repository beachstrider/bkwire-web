import { Box, Button } from '@mui/material';
import { Link, Navigate } from 'react-router-dom';
import { LoginButton } from '../../components/auth/LoginButton';
import { LogoutButton } from '../../components/auth/LogoutButton';
import { SignupButton } from '../../components/auth/SignupButton';
import { Hero } from './hero/Hero';
import { Quotes } from './quotes/Quotes';
import { Features } from './features/Features';
import { Concept } from './concept/Concept';
import { Partners } from './partners/Partners';
import { Coda } from './coda/Coda';
import { useAuth0 } from '@auth0/auth0-react';
import { Loading } from '../../components/loading/Loading';

const skipLandingPage = true;

export const LandingPageHeader = () => {
  const { isAuthenticated } = useAuth0();

  return (
    <>
      <Box flexGrow={1} />
      {isAuthenticated ? (
        <LogoutButton />
      ) : (
        <>
          <Button component={Link} to="">
            About
          </Button>
          <Button component={Link} to="/account/billing">
            Plans
          </Button>
          <Button
            onClick={() =>
              document.getElementById('why-bkwire')?.scrollIntoView()
            }
          >
            Why BKwire
          </Button>
          <LoginButton />
          <SignupButton />
        </>
      )}
    </>
  );
};

export const LandingPage = () => {
  const { isAuthenticated, isLoading } = useAuth0();

  return isLoading ? (
    <Loading />
  ) : isAuthenticated || skipLandingPage ? (
    <Navigate to="/dashboard" />
  ) : (
    <Box display="flex" flexDirection="column" flexGrow={1} width="inherit">
      <Hero />
      <Quotes />
      <Features />
      <Concept />
      <Partners />
      <Coda />
    </Box>
  );
};
