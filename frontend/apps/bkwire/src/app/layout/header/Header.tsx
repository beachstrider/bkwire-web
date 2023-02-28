import { Container, Toolbar, Box, useTheme } from '@mui/material';
import { Global } from '@emotion/react';
import { Logo } from '../logo/Logo';
import { Routes, Route } from 'react-router-dom';
import { MainMenu } from '../mainMenu/MainMenu';
import { Search } from '../search/Search';
import { SecondaryMenu } from '../secondaryMenu/SecondaryMenu';
import { LandingPageHeader } from '../../pages/landingPage/LandingPage';
import { OnboardingHeader } from '../../pages/onboarding/Onboarding';
import { headerGlobalStyles, HeaderRoot } from './Header.styled';
import { useAuth0 } from '@auth0/auth0-react';
import { useRouteUtils } from '../../hooks/useRouteUtils';
import { useScrollToTop } from '../../hooks/useScrollToTop';
import { TrialBadge } from './TrialBadge';
import { useGetViewer } from '../../api/api.hooks';

export const Header = () => {
  useScrollToTop();

  const theme = useTheme();
  const { isLoading } = useAuth0();
  const { isLoading: isViewerLoading } = useGetViewer();
  const { matchArea, matchPage } = useRouteUtils();

  const isLandingPage = matchPage('');
  const isOnboardingArea = matchArea('onboarding');

  const inverted = isLandingPage || isOnboardingArea;

  const height = isOnboardingArea
    ? theme.layout.headerTallHeight
    : theme.layout.headerHeight;

  return (
    <HeaderRoot
      position="fixed"
      elevation={0}
      height={height}
      inverted={inverted}
    >
      <Global styles={headerGlobalStyles(height)} />
      <Container maxWidth="lg">
        <Toolbar disableGutters>
          <Logo />
          {!isLoading && (
            <Routes>
              <Route index element={<LandingPageHeader />} />
              <Route path="onboarding/*" element={<OnboardingHeader />} />
              <Route
                path="*"
                element={
                  !isViewerLoading && (
                    <>
                      <MainMenu />
                      <Box flexGrow={1} />
                      <Search />
                      <SecondaryMenu />
                      <TrialBadge />
                    </>
                  )
                }
              />
            </Routes>
          )}
        </Toolbar>
      </Container>
    </HeaderRoot>
  );
};
