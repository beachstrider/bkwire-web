import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AppState, Auth0Provider } from '@auth0/auth0-react';

export const AuthProvider: React.FC = ({ children }) => {
  const domain = process.env.NX_APP_AUTH0_DOMAIN || '';
  const clientId = process.env.NX_APP_AUTH0_CLIENT_ID || '';
  const audience = process.env.NX_APP_AUTH0_AUDIENCE || '';
  const scope = process.env.NX_APP_AUTH0_SCOPE || '';

  const navigate = useNavigate();

  const onRedirect = (appState: AppState | undefined) => {
    navigate(appState?.returnTo || window.location.pathname);
  };

  return (
    <Auth0Provider
      domain={domain}
      clientId={clientId}
      redirectUri={window.location.origin}
      audience={audience}
      scope={scope}
      useRefreshTokens={true}
      onRedirectCallback={onRedirect}
    >
      {children}
    </Auth0Provider>
  );
};

export default AuthProvider;
