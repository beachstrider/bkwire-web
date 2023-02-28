import { Box, Tab, Typography } from '@mui/material';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { PagePaper } from '../../components/PagePaper.styled';
import { PageTabs } from '../../components/PageTabs.styled';
import { Elem, useLayoutUtils } from '../../hooks/useLayoutUtils';
import { useRouteUtils } from '../../hooks/useRouteUtils';
import { Alerts } from './Alerts';
import { Billing } from './Billing';
import { Industries } from './Industries';
import { Profile } from './Profile';
import { Team } from './Team';

const tabs = [
  { label: 'Profile', page: 'profile', element: <Profile /> },
  { label: 'Team', page: 'team', element: <Team /> },
  { label: 'Alerts', page: 'alerts', element: <Alerts /> },
  { label: 'BKwire Zones', page: 'industries', element: <Industries /> },
  { label: 'Billing', page: 'billing', element: <Billing /> },
];

export const Account = () => {
  const navigate = useNavigate();
  const { matchPage } = useRouteUtils();
  const { fillHeightCss } = useLayoutUtils();

  return (
    <Box flexGrow={1}>
      <Typography variant="h1" my={3}>
        My Account
      </Typography>
      <PageTabs
        value={tabs.findIndex((tab) => matchPage(tab.page))}
        onChange={(_, tabIndex) => navigate(tabs[tabIndex].page)}
      >
        {tabs.map((tab) => (
          <Tab key={tab.label} label={tab.label} />
        ))}
      </PageTabs>

      <PagePaper
        display="flex"
        mb={2}
        minHeight={fillHeightCss(Elem.Header | Elem.Heading | Elem.PageTabs)}
      >
        <Routes>
          {tabs.map((tab) => (
            <Route key={tab.label} path={tab.page} element={tab.element} />
          ))}
        </Routes>
      </PagePaper>
    </Box>
  );
};
