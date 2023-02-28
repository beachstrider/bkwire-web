import { useEffect } from 'react';
import {
  useAuth0,
  WithAuthenticationRequiredOptions,
} from '@auth0/auth0-react';
import { Loading } from '../loading/Loading';
import { Navigate } from 'react-router-dom';
import { useRouteUtils } from '../../hooks/useRouteUtils';
import { useGetViewer } from '../../api/api.hooks';

export const RequireAuth = ({
  options = {},
  children,
}: {
  options?: WithAuthenticationRequiredOptions;
  children?: JSX.Element;
}): JSX.Element => {
  const { user, isAuthenticated, isLoading, loginWithRedirect } = useAuth0();
  const {
    returnTo = `${window.location.pathname}${window.location.search}`,
    claimCheck = (): boolean => true,
    loginOptions,
  } = options;

  const routeIsAuthenticated = isAuthenticated && claimCheck(user);

  useEffect(() => {
    if (isLoading || routeIsAuthenticated) {
      return;
    }
    const opts = {
      ...loginOptions,
      appState: {
        ...(loginOptions && loginOptions.appState),
        returnTo: typeof returnTo === 'function' ? returnTo() : returnTo,
      },
    };
    (async (): Promise<void> => {
      await loginWithRedirect(opts);
    })();
  }, [
    isLoading,
    routeIsAuthenticated,
    loginWithRedirect,
    loginOptions,
    returnTo,
  ]);

  const { matchArea, matchPage } = useRouteUtils();
  const {
    data: viewer,
    isLoading: isViewerLoading,
    isRefetching: isViewerRefetching,
  } = useGetViewer();

  const isOnboarding = matchArea('onboarding');
  const isBilling = matchArea('account') && matchPage('billing');

  if (routeIsAuthenticated && viewer && !isViewerLoading) {
    // ensure subscription
    if (
      !isViewerRefetching &&
      !isBilling &&
      !isOnboarding &&
      viewer.subscription === 'none'
    ) {
      return <Navigate to="/account/billing" />;
    }

    // ensure onboarding
    if (!isViewerRefetching && isOnboarding && viewer.onboarding_completed) {
      return <Navigate to={{ pathname: '/dashboard' }} />;
    }

    if (!isViewerRefetching && !isOnboarding && !viewer.onboarding_completed) {
      return <Navigate to={{ pathname: '/onboarding/industries' }} />;
    }

    return children || <Navigate to={{ pathname: '/dashboard' }} />;
  } else {
    return <Loading />;
  }
};
