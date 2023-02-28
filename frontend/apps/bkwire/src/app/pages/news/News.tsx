import React, { useEffect } from 'react';
import { Box, ListItemButton, Typography } from '@mui/material';
import { PagePaper } from '../../components/PagePaper.styled';
import { Loading } from '../../components/loading/Loading';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import { NewsFilters } from './News.styled';
import { useGetNews, useGetIndustries } from '../../api/api.hooks';
import _groupBy from 'lodash/groupBy';
import { Elem, useLayoutUtils } from '../../hooks/useLayoutUtils';
import { formatDateRelative } from '../../utils/date';
import { NewsRoot } from './News.styled';
import { useQueryStringState } from '../../hooks/useQueryStringState';
import NewspaperIcon from '@mui/icons-material/Newspaper';

export const News: React.FC = () => {
  const { fillHeightCss } = useLayoutUtils();

  const { data: industries, isLoading: industriesLoading } = useGetIndustries();

  const [sector, setSector] = useQueryStringState<string>('sector', 'all');

  const { data, isLoading, refetch, isRefetching } = useGetNews(
    sector && sector !== 'all' ? Number(sector) : undefined
  );

  useEffect(() => {
    refetch();
  }, [refetch, sector]);

  return (
    <Box flexGrow={1}>
      <Box display="flex">
        <Typography variant="h1" my={3} display="inline-flex">
          BKwire News
        </Typography>
      </Box>

      <Box display="flex">
        <PagePaper width={240} mb={2} mr={2} flexShrink={0}>
          <Box display="flex" justifyContent="space-between" height={48} px={2}>
            <Typography variant="body2" fontWeight="bold" alignSelf="center">
              Sectors
            </Typography>
          </Box>
          <NewsFilters>
            {industriesLoading ? (
              <Box mt={10}>
                <Loading />
              </Box>
            ) : (
              <>
                <ListItemButton
                  selected={sector === 'all'}
                  onClick={() => setSector('all')}
                >
                  <NewspaperIcon />
                  <Typography variant="body2">All BK News</Typography>
                </ListItemButton>
                {industries
                  ?.filter((i) => i.value !== 13)
                  .map((i) => (
                    <ListItemButton
                      key={i.value}
                      selected={sector === i.value.toString()}
                      onClick={() => setSector(i.value.toString())}
                    >
                      {i.icon}
                      <Typography variant="body2">{i.text}</Typography>
                    </ListItemButton>
                  ))}
              </>
            )}
          </NewsFilters>
        </PagePaper>

        <PagePaper
          flexGrow={1}
          minHeight={fillHeightCss(Elem.Header | Elem.Heading)}
          mb={2}
        >
          {isLoading || isRefetching ? (
            <Loading />
          ) : (
            <>
              <Box p={2}>
                <Typography variant="body2" fontWeight="bold">
                  News articles -{' '}
                  {industries?.find((i) => i.value.toString() === sector)
                    ?.text || 'All sectors'}
                </Typography>
              </Box>
              {data && (
                <Box>
                  {data.map((n) => (
                    <NewsRoot
                      key={n.Link}
                      onClick={() => window.open(n.Link, '_blank')}
                    >
                      <Box className="news-content">
                        <Box className="news-icon">
                          <OpenInNewIcon />
                        </Box>
                        <Box className="news-body">
                          <Typography variant="body2" fontWeight="bold" mb={1}>
                            {n.Title}
                          </Typography>
                          <Typography variant="body2">{n.Snippet}</Typography>
                        </Box>
                        <Box className="news-actions">
                          <Typography variant="caption">
                            {formatDateRelative(n.date)}
                          </Typography>
                        </Box>
                      </Box>
                    </NewsRoot>
                  ))}
                </Box>
              )}
            </>
          )}
        </PagePaper>
      </Box>
    </Box>
  );
};
