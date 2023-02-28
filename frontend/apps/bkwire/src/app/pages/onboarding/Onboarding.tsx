import React from 'react';
import { Route, Routes } from 'react-router-dom';
import { Step, StepLabel, Stepper } from '@mui/material';
import { Industries } from './industries/Industries';
import { YourCompany } from './yourCompany/YourCompany';
import { Alerts } from './alerts/Alerts';
import { OnboardingRoot, StepperRoot } from './Onboarding.styled';
import { useRouteUtils } from '../../hooks/useRouteUtils';

export const OnboardingHeader: React.VFC = () => {
  const { matchPages } = useRouteUtils();

  const [isIndustries, isYourCompany, isAlerts] = matchPages([
    'industries',
    'yourcompany',
    'alerts',
  ]);

  const steps = [
    {
      key: 'Industries',
      active: isIndustries,
      completed: isAlerts || isYourCompany,
    },
    {
      key: 'Notifications',
      active: isAlerts,
      completed: isYourCompany,
    },
    {
      key: 'Your Company',
      active: isYourCompany,
      completed: false,
    },
  ];

  return (
    <StepperRoot>
      <Stepper alternativeLabel>
        {steps.map((stepProps) => (
          <Step {...stepProps}>
            <StepLabel>{stepProps.key}</StepLabel>
          </Step>
        ))}
      </Stepper>
    </StepperRoot>
  );
};

export const Onboarding: React.VFC = () => (
  <OnboardingRoot>
    <Routes>
      <Route path="industries" element={<Industries />} />
      <Route path="alerts" element={<Alerts />} />
      <Route path="yourcompany" element={<YourCompany />} />
    </Routes>
  </OnboardingRoot>
);
