import { Box, Tab, Typography } from '@mui/material';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { PageTabs } from '../../components/PageTabs.styled';
import { useRouteUtils } from '../../hooks/useRouteUtils';
import { CompaniesWatchlist } from './CompaniesWatchlist';
import { BankruptciesWatchlist } from './BankruptciesWatchlist';
import { PagePaper } from '../../components/PagePaper.styled';
import { Elem, useLayoutUtils } from '../../hooks/useLayoutUtils';

const tabs = [
  {
    label: 'Corporate Bankruptcies',
    page: 'bankruptcies',
    element: <BankruptciesWatchlist />,
  },
  {
    label: 'Impacted Businesses',
    page: 'companies',
    element: <CompaniesWatchlist />,
  },
];

export const Watchlist = () => {
  const navigate = useNavigate();
  const { matchPage } = useRouteUtils();
  const { fillHeightCss } = useLayoutUtils();

  return (
    <Box flexGrow={1}>
      <Typography variant="h1" my={3}>
        Watchlist
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
        flexDirection="column"
        minHeight={fillHeightCss(Elem.Header | Elem.Heading | Elem.PageTabs)}
        mb={2}
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
