import { Box, Tab, Typography } from '@mui/material';
import { useMemo, useState } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { PageTabs } from '../../components/PageTabs.styled';
import { ZoneFilter } from '../../components/zoneFilter/ZoneFilter';
import { ZoneFilterContainer } from '../../components/zoneFilter/ZoneFilter.styled';
import { useHorizontalScroll } from '../../hooks/useHorizontalScroll';
import { Elem, useLayoutUtils } from '../../hooks/useLayoutUtils';
import { useRouteUtils } from '../../hooks/useRouteUtils';
import { Bankruptcies } from './bankruptcies/Bankruptcies';
import { Losses } from './losses/Losses';

export const List = () => {
  const navigate = useNavigate();
  const { matchPage } = useRouteUtils();
  const { fillHeightCss } = useLayoutUtils();

  const [industriesFilter, setIndustriesFilter] = useState<number[]>([]);

  const tabs = useMemo(
    () => [
      {
        label: 'Corporate Bankruptcy',
        page: 'bankruptcies',
        element: <Bankruptcies industriesFilter={industriesFilter} />,
      },
      {
        label: 'Impacted Businesses',
        page: 'losses',
        element: <Losses industriesFilter={industriesFilter} />,
      },
    ],
    [industriesFilter]
  );

  const horizontalScrollElRef = useHorizontalScroll();

  return (
    <Box flexGrow={1} maxWidth="100%" pt={3}>
      {/* <Typography variant="h1" my={3} display="inline-flex">
        All Corporate Bankruptcy & Impacted Businesses
      </Typography> */}

      <PageTabs
        value={tabs.findIndex((tab) => matchPage(tab.page))}
        onChange={(_, tabIndex) => navigate(tabs[tabIndex].page)}
      >
        {tabs.map((tab) => (
          <Tab key={tab.label} label={tab.label} sx={{ flexShrink: 0 }} />
        ))}
        <ZoneFilterContainer ml={2} ref={horizontalScrollElRef}>
          <ZoneFilter
            industriesFilter={industriesFilter}
            setIndustriesFilter={setIndustriesFilter}
          />
        </ZoneFilterContainer>
      </PageTabs>

      <Box
        display="flex"
        minHeight={fillHeightCss(Elem.Header | Elem.PageTabs, 5)}
        // minHeight={fillHeightCss(Elem.Header | Elem.Heading | Elem.PageTabs)}
        mb={2}
      >
        <Routes>
          {tabs.map((tab) => (
            <Route key={tab.label} path={tab.page} element={tab.element} />
          ))}
        </Routes>
      </Box>
    </Box>
  );
};
