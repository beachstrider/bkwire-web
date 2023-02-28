import { useRef, useCallback, useMemo, useState, useEffect } from 'react';
import {
  GridActionsCellItem,
  GridColDef,
  GridColumnVisibilityModel,
  GridRowId,
  GridRowParams,
  GridSlotsComponent,
  GridSortModel,
} from '@mui/x-data-grid';
import ShareIcon from '@mui/icons-material/ShareOutlined';
import AddWatchlist from '@mui/icons-material/PlaylistAdd';
import RemoveWatchlist from '@mui/icons-material/PlaylistAddCheck';
import { DataGrid, GridToolbar } from '../../../components/dataGrid/DataGrid';
import { LossFilters, LossSorting } from '../../../api/api.types';
import { Share, ShareHandle } from '../../../components/share/Share';
import {
  useAddToCompaniesWatchlist,
  useGetCompaniesWatchlist,
  useGetCorporateLosses,
  useGetIndustries,
  useRemoveFromCompaniesWatchlist,
} from '../../../api/api.hooks';
import { useFormatters } from '../../../hooks/useFormatters';
import { useDebounce } from '../../../hooks/useDebounce';
import { CircularProgress, Tooltip } from '@mui/material';

const SUMMARY_PAGE_SIZE = 15;

type GridMode = 'list' | 'watchlist' | 'summary';

interface LossesGridProps {
  industriesFilter: number[];
  filters: LossFilters;
  setFilters?: React.Dispatch<React.SetStateAction<LossFilters>>;
  mode?: GridMode;
  showBankruptcyColumn?: boolean;
  showCaption?: boolean;
  setCreditorsCount?: React.Dispatch<React.SetStateAction<number>>;
  components?: Partial<GridSlotsComponent>;
}
export const LossesGrid = ({
  industriesFilter,
  filters,
  setFilters,
  mode = 'list',
  showBankruptcyColumn = true,
  showCaption = true,
  setCreditorsCount,
  components,
}: LossesGridProps) => {
  const {
    mutate: addToWatchlist,
    isLoading: addToWatchlistLoading,
    variables: currentAddToWatchlistId,
  } = useAddToCompaniesWatchlist();
  const {
    mutate: removeFromWatchlist,
    isLoading: removeFromWatchlistLoading,
    variables: currentRemoveFromWatchlistId,
  } = useRemoveFromCompaniesWatchlist();

  const toggleWatchlistLoading =
    addToWatchlistLoading || removeFromWatchlistLoading;

  const shareModal = useRef<ShareHandle>(null);

  const isSummary = mode === 'summary';
  const isWatchlist = mode === 'watchlist';

  const {
    industryFormatter,
    industryValueFormatter,
    naFormatter,
    naValueFormatter,
    dateFormatter,
    linkFormatter,
    amountFormatter,
    amountValueFormatter,
  } = useFormatters();

  const toggleWatchlist = useCallback(
    (id: GridRowId, isWatchlisted: boolean) => () => {
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
  const share = useCallback(
    (lossId: GridRowId, caseId: GridRowId) => () => {
      shareModal.current?.open(
        `${window.location.origin}/view/bankruptcy/${caseId}`,
        lossId.toString(),
        'loss'
      );
    },
    []
  );

  const getActions = useCallback(
    (params: GridRowParams) => {
      const actions = [
        <GridActionsCellItem
          icon={
            (addToWatchlistLoading && currentAddToWatchlistId === params.id) ||
            (removeFromWatchlistLoading &&
              currentRemoveFromWatchlistId === params.id) ? (
              <CircularProgress size={20} />
            ) : (
              <Tooltip
                title={
                  isWatchlist || params.row.is_company_watchlisted
                    ? 'Remove from watchlist'
                    : 'Add to watchlist'
                }
                placement="top"
                disableInteractive
                arrow
              >
                {isWatchlist || params.row.is_company_watchlisted ? (
                  <RemoveWatchlist />
                ) : (
                  <AddWatchlist />
                )}
              </Tooltip>
            )
          }
          label="Toggle watchlist"
          onClick={toggleWatchlist(
            params.id,
            isWatchlist || params.row.is_company_watchlisted
          )}
        />,
      ];
      if (!isWatchlist) {
        actions.push(
          <GridActionsCellItem
            icon={
              <Tooltip title="Share" placement="top" disableInteractive arrow>
                <ShareIcon />
              </Tooltip>
            }
            label="Share"
            onClick={share(params.row.id, params.row.dci_id)}
          />
        );
      }
      return actions;
    },
    [
      addToWatchlistLoading,
      currentAddToWatchlistId,
      currentRemoveFromWatchlistId,
      isWatchlist,
      removeFromWatchlistLoading,
      share,
      toggleWatchlist,
    ]
  );

  const columns: GridColDef[] = useMemo(() => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const result: any[] = [
      {
        field: 'date_added',
        headerName: 'Date Added',
        headerAlign: 'left',
        align: 'left',
        width: 100,
        type: 'date',
        hideable: true,
        resizable: false,
        renderCell: dateFormatter,
      },
      {
        field: 'date_filed',
        headerName: 'Date Filed',
        headerAlign: 'left',
        align: 'left',
        width: 100,
        type: 'date',
        hideable: true,
        hide: true,
        resizable: false,
        renderCell: dateFormatter,
      },
      {
        field: 'creditor_name',
        headerName: 'Impacted Business',
        headerAlign: 'left',
        align: 'left',
        flex: 1.17,
        minWidth: 200,
        type: 'string',
        hideable: false,
        resizable: false,
      },
      {
        field: 'industry',
        headerName: 'BKwire Zone',
        headerAlign: 'left',
        align: 'left',
        width: 160,
        type: 'string',
        hideable: true,
        resizable: false,
        valueFormatter: industryValueFormatter,
        renderCell: industryFormatter,
      },
      {
        field: 'city',
        headerName: 'City',
        headerAlign: 'left',
        align: 'left',
        width: 120,
        type: 'string',
        hideable: true,
        resizable: false,
        valueFormatter: naValueFormatter,
        renderCell: naFormatter,
      },
      {
        field: 'state_code',
        headerName: 'State',
        headerAlign: 'left',
        align: 'left',
        width: 54,
        type: 'string',
        hideable: true,
        resizable: false,
        valueFormatter: naValueFormatter,
        renderCell: naFormatter,
      },
      {
        field: 'case_number',
        headerName: 'Case Number',
        headerAlign: 'left',
        align: 'left',
        flex: 1,
        type: 'string',
        hideable: true,
        resizable: false,
        renderCell: naFormatter,
      },      
      {
        field: 'case_name',
        headerName: 'Corporate Bankruptcy',
        headerAlign: 'left',
        align: 'left',
        flex: 1,
        type: 'string',
        hide: isWatchlist || !showBankruptcyColumn,
        hideable: true,
        resizable: false,
        renderCell: linkFormatter('/view/bankruptcy', 'dci_id'),
      },   
      {
        field: 'unsecured_claim',
        headerName: 'Loss',
        headerAlign: 'left',
        align: 'left',
        width: 130,
        type: 'number',
        hide: isWatchlist,
        hideable: !isWatchlist,
        resizable: false,
        valueFormatter: amountValueFormatter,
        renderCell: amountFormatter,
      },
      {
        field: 'Actions',
        type: 'actions',
        width: 80,
        hideable: false,
        hideSortIcons: true,
        disableExport: true,
        disableReorder: true,
        sortable: false,
        filterable: false,
        groupable: false,
        getActions,
      },
    ];
    if (isWatchlist) {
      result.splice(5, 2); // remove case and amount
    }
    return result;
  }, [
    dateFormatter,
    industryValueFormatter,
    industryFormatter,
    naValueFormatter,
    naFormatter,
    isWatchlist,
    showBankruptcyColumn,
    linkFormatter,
    amountValueFormatter,
    amountFormatter,
    getActions,
  ]);

  const [cvm, setCvm] = useState<GridColumnVisibilityModel>({
    date_added: true,
    date_filed: false,
    creditor_name: true,
    industry: true,
    city: true,
    state_code: true,
    case_number: false,
    case_name: !isWatchlist && showBankruptcyColumn,
    unsecured_claim: !isWatchlist,
    Actions: true,
  });

  const onColumnVisibilityModelChange = useCallback(
    (newCvm: GridColumnVisibilityModel) => {
      setCvm({
        ...newCvm,
        date_added: true,
        creditor_name: true,
        //case_name: !isWatchlist && showBankruptcyColumn,
        //...(isWatchlist ? { unsecured_claim: isWatchlist } : {}),
        Actions: true,
      
      });
    },
    [setCvm, isWatchlist, showBankruptcyColumn]
  );

  // NOTE: this would hide the case column entirely
  // but then it wouldn't show up in the export
  // if (!showBankruptcyColumn) {
  //   columns.splice(
  //     columns.findIndex((c) => c.field === 'case_name'),
  //     1
  //   );
  // }

  const [pageSize, setPageSize] = useState(50);
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState(filters.search);
  const [sortModel, setSortModel] = useState<GridSortModel>([
    {
      field: setCreditorsCount ? 'unsecured_claim' : 'date_added',
      sort: 'desc',
    },
  ]);

  const debouncedSearch = useDebounce(search, 400);

  useEffect(() => {
    setFilters?.((prevFilters) => ({
      ...prevFilters,
      search: debouncedSearch,
    }));
  }, [debouncedSearch, setFilters]);

  useEffect(() => setSearch(filters.search), [filters]);

  const itemsPerPage = isSummary ? SUMMARY_PAGE_SIZE : pageSize;
  const sorting = sortModel[0] as LossSorting;

  // NOTE: disabled the 'using hooks in conditionals' warning because
  //       the isWatchlist never changes once the component is created
  const { isLoading: rowsLoading, data } = isWatchlist
    ? // eslint-disable-next-line react-hooks/rules-of-hooks
      useGetCompaniesWatchlist(
        page + 1,
        itemsPerPage,
        filters,
        sorting,
        debouncedSearch || undefined
      )
    : // eslint-disable-next-line react-hooks/rules-of-hooks
      useGetCorporateLosses(
        page + 1,
        itemsPerPage,
        filters,
        industriesFilter,
        sorting,
        debouncedSearch || undefined
      );

  if (search === '' && !rowsLoading) {
    setCreditorsCount?.(data?.count || 0);
  }

  const { data: industries, isLoading: industriesLoading } = useGetIndustries();

  const { data: restData, isLoading: restDataLoading } = useGetCorporateLosses(
    1,
    SUMMARY_PAGE_SIZE,
    filters,
    industries
      ?.map((i) => i.value)
      .filter((i) => industriesFilter.indexOf(i) === -1) || [],
    sorting,
    '',
    isSummary && !industriesLoading
  );

  let count = data?.count || 0;
  const records = [...(data?.records || [])];
  if (
    isSummary &&
    restData &&
    !rowsLoading &&
    !restDataLoading &&
    count < SUMMARY_PAGE_SIZE
  ) {
    const restCount = Math.min(SUMMARY_PAGE_SIZE - count, restData.count);
    records.push(
      ...restData.records
        .slice(0, restCount)
        .map((r) => ({ ...r, isRest: true }))
    );
    count += restCount;
  }

  return (
    <>
      <DataGrid
        rows={records}
        columns={columns}
        columnVisibilityModel={cvm}
        onColumnVisibilityModelChange={onColumnVisibilityModelChange}
        disableColumnMenu
        getRowId={(r) => r.id}
        getRowClassName={(params) => (params.row.isRest ? 'rest-row' : '')}
        hideFooter={isSummary}
        rowCount={count}
        pageSize={isSummary ? SUMMARY_PAGE_SIZE : pageSize}
        onPageSizeChange={setPageSize}
        page={page}
        onPageChange={setPage}
        sortModel={sortModel}
        onSortModelChange={setSortModel}
        loading={rowsLoading}
        components={{
          Toolbar: GridToolbar,
          ...components,
        }}
        componentsProps={{
          toolbar: {
            header: isSummary ? { text: 'Impacted Businesses' } : undefined,
            search: isSummary
              ? undefined
              : {
                  search,
                  setSearch,
                  placeholder: 'Search Impacted Business…',
                },
            export: isSummary
              ? undefined
              : {
                  csvOptions: {
                    allColumns: true,
                  },
                },
            refreshActivities: !setCreditorsCount
              ? undefined
              : {
                  caseId: filters.id,
                },
            caption:
              isSummary || !showCaption
                ? undefined
                : {
                    text: isWatchlist
                      ? "BKwire's Watchlist notifies you when the company followed files or is impacted by future bankruptcies."
                      : 'Impacted companies are suppliers, banks, investors, and others named unsecured. No Collateral or assurance of payment.',
                  },
          },
        }}
      />
      <Share ref={shareModal} />
    </>
  );
};
