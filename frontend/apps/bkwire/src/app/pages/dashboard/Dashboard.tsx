import React, { useState } from 'react';
import { Box, Typography } from '@mui/material';
import { PagePaper } from '../../components/PagePaper.styled';
import { useHelpWizard } from '../../providers/HelpWizardProvider';
import { BankruptcyFilters, LossFilters } from '../../api/api.types';
import { BankruptciesGrid } from '../list/bankruptcies/BankruptciesGrid';
import { LossesGrid } from '../list/losses/LossesGrid';
import { Histogram } from '../../components/histogram/Histogram';
import { useGetHistogram, useGetNews, useGetViewer } from '../../api/api.hooks';
import { GridSummaryPaper, NewsItem } from './Dashboard.styled';
import { ButtonLink } from '../../components/ButtonLink';
import { defaultLossFilters } from '../list/losses/LossesFilters';
import { defaultBkFilters } from '../list/bankruptcies/BankruptciesFilters';
import { Loading } from '../../components/loading/Loading';
import { ZoneFilter } from '../../components/zoneFilter/ZoneFilter';
import { useHorizontalScroll } from '../../hooks/useHorizontalScroll';
import { ZoneFilterContainer } from '../../components/zoneFilter/ZoneFilter.styled';

export const Dashboard = () => {
  const { data: viewer, isLoading: viewerLoading } = useGetViewer();
  const { data: news, isLoading: newsLoading } = useGetNews();
  const { data: bkHistogram, isLoading: bkHistogramLoading } =
    useGetHistogram();

  const isLoading = viewerLoading || newsLoading || bkHistogramLoading;

  const [filters] = useState<{
    bk: BankruptcyFilters;
    loss: LossFilters;
  }>({
    bk: defaultBkFilters,
    loss: {
      ...defaultLossFilters,
      max_losses_per_case: 3,
    },
  });

  const [industriesFilter, setIndustriesFilter] = useState<number[]>([]);

  const horizontalScrollElRef = useHorizontalScroll();

  return isLoading ? (
    <Loading />
  ) : (
    <Box display="flex" flexDirection="column" flexGrow={1} maxWidth="100%">
      <Typography variant="h1" mb={1}>
        Hello {viewer?.first_name},
      </Typography>
      <Typography variant="h3" mb={3}>
        Welcome - You are reviewing the most up to date Corporate Bankruptcies and
        Impacted Businesses
      </Typography>

      <ZoneFilterContainer ref={horizontalScrollElRef}>
        <ZoneFilter
          industriesFilter={industriesFilter}
          setIndustriesFilter={setIndustriesFilter}
        />
      </ZoneFilterContainer>

      <Box mb={3} mt={2} display="flex" minHeight={340}>
        <PagePaper display="flex" flexDirection="column" flexGrow={1}>
          <Box p={2}>
            <Typography variant="h2">
              Corporate Bankruptcy Filings Last 30 Days
            </Typography>
          </Box>
          <Box flexGrow={1}>
            <Histogram
              xLabel="Number of bankruptcies"
              yLabel="Days"
              legend="Number of new filings"
              loading={bkHistogramLoading}
              columns={bkHistogram?.days || []}
              lastDate={bkHistogram?.lastDate}
            />
          </Box>
        </PagePaper>
        <PagePaper p={2} ml={2} width={380} maxHeight={340}>
          <Box display="flex">
            <Typography variant="h2" flexGrow={1}>
              BKwire Zone News
            </Typography>
            <ButtonLink to="/news">View all</ButtonLink>
          </Box>
          {!news || newsLoading ? (
            <Loading />
          ) : (
            <Box display="flex" flexDirection="column" mt={2}>
              {news.slice(0, 7).map((n) => (
                <NewsItem
                  key={n.Link}
                  onClick={() => window.open(n.Link, '_blank')}
                >
                  {n.Title}
                </NewsItem>
              ))}
            </Box>
          )}
        </PagePaper>
      </Box>

      <GridSummaryPaper>
        <BankruptciesGrid
          filters={filters.bk}
          industriesFilter={industriesFilter}
          mode="summary"
        />
        <Box className="view-all">
          <ButtonLink to="/list/bankruptcies">
            View all Corporate Bankruptcies
          </ButtonLink>
        </Box>
      </GridSummaryPaper>

      <GridSummaryPaper>
        <LossesGrid
          filters={filters.loss}
          industriesFilter={industriesFilter}
          mode="summary"
        />
        <Box className="view-all">
          <ButtonLink to="/list/losses">
            View all Impacted Businesses
          </ButtonLink>
        </Box>
      </GridSummaryPaper>
    </Box>
  );
};
