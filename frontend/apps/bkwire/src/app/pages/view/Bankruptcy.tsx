import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  AddCircleOutlineOutlined,
  ArticleOutlined,
  GavelOutlined,
  InfoOutlined,
  ListAltOutlined,
  PrecisionManufacturingOutlined,
  RemoveCircleOutlineOutlined,
  TrendingDownOutlined,
  PictureAsPdfRounded,
  ReadMoreOutlined,
  ShareOutlined,
  DocumentScannerSharp,
} from '@mui/icons-material';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  useTheme,
  CircularProgress,
} from '@mui/material';
import { ButtonLink } from '../../components/ButtonLink';
import { LossFilters } from '../../api/api.types';
import { LossesGrid } from '../list/losses/LossesGrid';
import {
  InfoBox,
  InfoBoxContent,
  InfoBoxContentProps,
  InfoBoxProps,
} from './View';
import { PageGrid } from '../../components/PageGrid.styled';
import {
  useAddToBankruptciesWatchlist,
  useGetBankruptcy,
  useRemoveFromBankruptciesWatchlist,
} from '../../api/api.hooks';
import { useParams } from 'react-router';
import dateFormat from 'date-fns/format';
import { formatAmount, formatRangeKMB } from '../../utils/number';
import { Share, ShareHandle } from '../../components/share/Share';
import form201Img from '../../../assets/form201.png';
import { Form201Icon, TabBox } from './View.styled';
import useApi from '../../api/api.client';
import { defaultLossFilters } from '../list/losses/LossesFilters';
import { ActivitiesGrid } from './ActivitiesGrid';
import { FileDownload, FileDownloadHandle } from './FileDownload';
import { toDateSafe } from '../../utils/date';

enum TabTypes {
  Creditors = 0,
  Docket = 1,
}

export const Bankruptcy: React.VFC = () => {
  const theme = useTheme();
  const params = useParams();

  const id = Number.parseInt(params.id || '');

  const { mutate: addToWatchlist, isLoading: addToWatchlistLoading } =
    useAddToBankruptciesWatchlist();
  const { mutate: removeFromWatchlist, isLoading: removeFromWatchlistLoading } =
    useRemoveFromBankruptciesWatchlist();

  const toggleWatchlistLoading =
    addToWatchlistLoading || removeFromWatchlistLoading;

  const shareModal = useRef<ShareHandle>(null);
  const filesModal = useRef<FileDownloadHandle>(null);

  const [tab, setTab] = useState(TabTypes.Creditors);
  const [creditorsCount, setCreditorsCount] = useState(0);

  const [filters, setFilters] = useState<LossFilters>({
    ...defaultLossFilters,
    id,
  });

  const [infos, setInfos] = useState<
    { type: InfoBoxProps; content: InfoBoxContentProps }[]
  >([]);

  const { data } = useGetBankruptcy(id);

  useEffect(() => {
    setFilters({
      ...defaultLossFilters,
      id,
    });
  }, [id]);

  useEffect(() => {
    if (data) {
      const result: { type: InfoBoxProps; content: InfoBoxContentProps }[] = [];

      if (data.assets_min !== null && data.assets_max) {
        result.push({
          type: { title: 'Assets ($)', icon: <AddCircleOutlineOutlined /> },
          content: {
            value:
              data.assets_min === -1
                ? 'see petition'
                : formatRangeKMB({
                    min: data.assets_min,
                    max: data.assets_max,
                  }),
          },
        });
      }

      if (data.liabilities_min !== null && data.liabilities_max) {
        result.push({
          type: {
            title: 'Liabilities ($)',
            icon: <RemoveCircleOutlineOutlined />,
          },
          content: {
            value:
              data.liabilities_min === -1
                ? 'see petition'
                : formatRangeKMB({
                    min: data.liabilities_min,
                    max: data.liabilities_max,
                  }),
          },
        });
      }

      if (data.industry) {
        result.push({
          type: {
            title: 'BKwire Zone',
            icon: <PrecisionManufacturingOutlined />,
          },
          content: { value: data.industry },
        });
      }

      if (data.ein) {
        result.push({
          type: { title: 'Federal EIN', icon: <ArticleOutlined /> },
          content: { value: data.ein.toString() },
        });
      }

      if (data.court_id !== null) {
        result.push({
          type: {
            title: 'Court',
            icon: <GavelOutlined />,
          },
          content: {
            value: data.court_id,
          },
        });
      }

      setInfos(result);
    }
  }, [data]);

  const gridRowHeight = 153;
  const tabBoxRowSpan = Math.max(3, infos.length - 2);
  const tabBoxHeight =
    tabBoxRowSpan * gridRowHeight + (tabBoxRowSpan - 1) * theme.layout.gutter;

  const { get } = useApi();

  const showPdf = useCallback(async () => {
    if (data?.dci_id) {
      try {
        const { data: url } = await get<string>('/pdf-form', {
          params: { id: data.dci_id },
        });

        window.open(url, '_blank');
      } catch {
        console.log('Something went wrong!');
      }
    }
  }, [data?.dci_id, get]);

  const toggleWatchlist = useCallback(
    (id: number, isWatchlisted: boolean) => {
      if (!toggleWatchlistLoading) {
        if (isWatchlisted) {
          removeFromWatchlist(Number(id));
        } else {
          addToWatchlist(Number(id));
        }
      }
    },
    [addToWatchlist, removeFromWatchlist, toggleWatchlistLoading]
  );

  const NoRows = () => (
    <Box
      width="100%"
      height="100%"
      display="flex"
      justifyContent="center"
      alignItems="center"
    >
      {!!data &&
        (data.is_bankruptcy_watchlisted ? (
          <Box display="flex" flexDirection="column" alignItems="center">
            <Typography variant="h1">The case is in your watchlist.</Typography>
            <Typography variant="h3">
              We will notify you as soon as new data comes in.
            </Typography>
          </Box>
        ) : (
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            zIndex={100}
            sx={{ pointerEvents: 'all' }}
          >
            <Typography variant="h1">
              Impacted Businesses not available yet.
            </Typography>
            <ButtonLink
              endIcon={
                toggleWatchlistLoading ? (
                  <CircularProgress size={20} />
                ) : (
                  <ListAltOutlined />
                )
              }
              onClick={() =>
                toggleWatchlist(
                  data.dci_id,
                  Boolean(data.is_bankruptcy_watchlisted)
                )
              }
              sx={{ fontSize: 20 }}
            >
              Click here to move case to your watchlist.
            </ButtonLink>
          </Box>
        ))}
    </Box>
  );

  return (
    <Box display="flex" flexDirection="column" gap={2} flexGrow={1}>
      <Box display="flex">
        <Box>
          <Typography variant="h1" display="block" minHeight="unset" mb={1}>
            {data?.case_name}
          </Typography>
          <Typography variant="body1" color={(t) => t.palette.grey[600]} mb={2}>
            {[data?.company_address, data?.city, data?.state_code]
              .filter((x) => x)
              .join(', ')}
          </Typography>
        </Box>
        <Box
          display="flex"
          gap={4}
          flexGrow={1}
          justifyContent="end"
          alignItems="start"
          pt={4}
        >
          {!!data && (
            <>
              <ButtonLink
                endIcon={<DocumentScannerSharp />}
                onClick={() => filesModal.current?.open(id)}
              >
                My Files
              </ButtonLink>
              <ButtonLink
                endIcon={
                  toggleWatchlistLoading ? (
                    <CircularProgress size={20} />
                  ) : (
                    <ListAltOutlined />
                  )
                }
                onClick={() =>
                  toggleWatchlist(
                    data.dci_id,
                    Boolean(data.is_bankruptcy_watchlisted)
                  )
                }
              >
                {data.is_bankruptcy_watchlisted
                  ? 'Remove from Watchlist'
                  : 'Add to Watchlist'}
              </ButtonLink>
              <ButtonLink
                endIcon={<ShareOutlined />}
                onClick={() =>
                  shareModal.current?.open(
                    `${window.location.origin}/view/bankruptcy/${id}`,
                    id.toString(),
                    'bk'
                  )
                }
              >
                Share
              </ButtonLink>
            </>
          )}
        </Box>
      </Box>

      <PageGrid columns={4}>
        {infos.map((i, index) => (
          <InfoBox
            key={i.type.title}
            gridRow={index + 1}
            gridColumn="1"
            {...i.type}
            height={gridRowHeight}
          >
            <InfoBoxContent {...i.content} />
          </InfoBox>
        ))}
        <InfoBox
          gridRow="1"
          gridColumn="2 / span 2"
          title={'Bankruptcy details'}
          icon={<TrendingDownOutlined />}
        >
          <Box display="flex" flexGrow={1} gap={2}>
            <InfoBoxContent
              label={'Chapter type'}
              value={data?.cs_chapter.toString() || 'pending'}
              caption={
                data?.cs_chapter && data?.cs_chapter === 11
                  ? 'Business reorganization'
                  : 'Liquidation'
              }
              width="40%"
            />
            <InfoBoxContent
              label={'Case number'}
              value={data?.case_number || 'pending'}
              caption={
                data?.date_filed &&
                `Filed on ${dateFormat(
                  toDateSafe(data.date_filed),
                  'MM-dd-yy'
                )}`
              }
              color={(t) => t.palette.link.light}
              labelAdornment={<InfoOutlined />}
              width="60%"
              onClick={() => setTab(TabTypes.Docket)}
            />
          </Box>
        </InfoBox>
        <InfoBox
          gridRow="2"
          gridColumn="2 / span 2"
          title={'Loss information'}
          icon={<RemoveCircleOutlineOutlined />}
        >
          <Box display="flex" flexGrow={1} gap={2}>
            <InfoBoxContent
              label={'Creditors'}
              value={
                data?.creditor_min === -1
                  ? 'see petition'
                  : formatRangeKMB({
                      min: data?.creditor_min || 0,
                      max: data?.creditor_max || 49,
                    })
              }
              width="40%"
            />
            <InfoBoxContent
              label={'Unsecured amount'}
              value={formatAmount(data?.total_loss || 0)}
              caption={`from ${creditorsCount} creditors`}
              width="60%"
            />
          </Box>
        </InfoBox>
        <Form201Icon
          gridRow="1 / span 2"
          gridColumn="4"
          imgSrc={form201Img}
          onClick={showPdf}
        >
          <div className="hint">
            <PictureAsPdfRounded />
            <Typography variant="h3">Click here for petition</Typography>
          </div>
        </Form201Icon>
        <TabBox
          gridRow={`3 / span ${tabBoxRowSpan}`}
          gridColumn="2 / span 3"
          height={tabBoxHeight}
        >
          <Tabs value={tab} onChange={(_, t) => setTab(t)}>
            <Tab
              label={`${creditorsCount} unsecured creditors`}
              icon={<TrendingDownOutlined />}
              iconPosition="start"
            />
            <Tab
              label="Case Information"
              icon={<ReadMoreOutlined />}
              iconPosition="start"
            />
          </Tabs>

          <Box flexGrow={1} hidden={tab !== TabTypes.Creditors}>
            <LossesGrid
              filters={filters}
              industriesFilter={[]}
              showBankruptcyColumn={false}
              showCaption={false}
              setCreditorsCount={setCreditorsCount}
              components={{
                NoRowsOverlay: NoRows,
              }}
            />
          </Box>

          {tab === TabTypes.Docket && (
            <Box flexGrow={1}>
              <ActivitiesGrid
                caseId={id}
                components={{
                  NoRowsOverlay: NoRows,
                }}
              />
            </Box>
          )}
        </TabBox>
      </PageGrid>
      <Share ref={shareModal} />
      <FileDownload ref={filesModal} />
    </Box>
  );
};
