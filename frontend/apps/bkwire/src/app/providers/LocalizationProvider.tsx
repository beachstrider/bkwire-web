import React from 'react';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider as MuiLocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';

export const LocalizationProvider: React.FC = ({ children }) => (
  <MuiLocalizationProvider dateAdapter={AdapterDateFns}>
    {children}
  </MuiLocalizationProvider>
);

export default LocalizationProvider;
