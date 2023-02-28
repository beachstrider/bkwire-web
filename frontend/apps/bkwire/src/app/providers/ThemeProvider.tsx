import React from 'react';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import { Global } from '@emotion/react';
import { CssBaseline } from '@mui/material';
import { globalStyles } from '../app.styled';
import theme from '../theme/theme';

export const ThemeProvider: React.FC = ({ children }) => (
  <MuiThemeProvider theme={theme}>
    <CssBaseline />
    <Global styles={globalStyles} />
    {children}
  </MuiThemeProvider>
);

export default ThemeProvider;
