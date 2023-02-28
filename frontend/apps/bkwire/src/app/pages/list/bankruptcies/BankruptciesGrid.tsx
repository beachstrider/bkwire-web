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
import { Share, ShareHandle } from '../../../components/share/Share';
import { BankruptcyFilters, BankruptcySorting } from '../../../api/api.types';
import {
  useAddToBankruptciesWatchlist,
  useGetBankruptcies,
  useGetBankruptciesWatchlist,
  useGetIndustries,
  useRemoveFromBankruptciesWatchlist,
} from '../../../api/api.hooks';
import { useFormatters } from '../../../hooks/useFormatters';
import { useDebounce } from '../../../hooks/useDebounce';
import { CircularProgress, Tooltip } from '@mui/material';
import { FastField } from 'formik';

const SUMMARY_PAGE_SIZE = 15;

type GridMode = 'list' | 'watchlist' | 'summary';

interface BankruptciesGridProps {
  industriesFilter: number[];
  filters: BankruptcyFilters;
  setFilters?: React.Dispatch<React.SetStateAction<BankruptcyFilters>>;
  mode?: GridMode;
  components?: Partial<GridSlotsComponent>;
}
export const BankruptciesGrid = ({
  industriesFilter,
  filters,
  setFilters,
  mode = 'list',
  components,
}: BankruptciesGridProps) => {
  const {
    mutate: addToWatchlist,
    isLoading: addToWatchlistLoading,
    variables: currentAddToWatchlistId,
  } = useAddToBankruptciesWatchlist();
  const {
    mutate: removeFromWatchlist,
    isLoading: removeFromWatchlistLoading,
    variables: currentRemoveFromWatchlistId,
  } = useRemoveFromBankruptciesWatchlist();

  const toggleWatchlistLoading =
    addToWatchlistLoading || removeFromWatchlistLoading;

  const shareModal = useRef<ShareHandle>(null);

  const isSummary = mode === 'summary';
  const isWatchlist = mode === 'watchlist';

  const {
    industryFormatter,
    industryValueFormatter,
    ctFormatter,
    ctValueFormatter,
    naFormatter,
    naValueFormatter,
    dateFormatter,
    linkFormatter,
    rangeFormatter,
    rangeValueFormatter,
    rangeFormatterKMB,
    rangeValueFormatterKMB,
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
    (id: GridRowId) => () => {
      shareModal.current?.open(
        `${window.location.origin}/view/bankruptcy/${id}`,
        id.toString(),
        'bk'
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
                  isWatchlist || params.row.is_bankruptcy_watchlisted
                    ? 'Remove from watchlist'
                    : 'Add to watchlist'
                }
                placement="top"
                disableInteractive
                arrow
              >
                {isWatchlist || params.row.is_bankruptcy_watchlisted ? (
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
            isWatchlist || params.row.is_bankruptcy_watchlisted
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
            onClick={share(params.id)}
          />
        );
      }
      return actions;
    },
    [
      addToWatchlistLoading,
      currentAddToWatchlistId,
      isWatchlist,
      removeFromWatchlistLoading,
      currentRemoveFromWatchlistId,
      share,
      toggleWatchlist,
    ]
  );

  const columns: GridColDef[] = useMemo(
    () => [
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
        field: 'case_number',
        headerName: 'Case Number',
        headerAlign: 'left',
        align: 'left',
        flex: 1,
        minWidth: 200,
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
        minWidth: 200,
        type: 'string',
        hideable: false,
        resizable: false,
        renderCell: linkFormatter('/view/bankruptcy', 'dci_id'),
      },    
      {
        field: 'industry',
        headerName: 'BKwire Zone',
        headerAlign: 'left',
        align: 'left',
        width: 160,
        type: 'string',
        hide: !isSummary,
        hideable: true,
        sortable: true,
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
        hide: !isSummary,
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
        field: 'cs_chapter',
        headerName: 'Chapter Type',
        headerAlign: 'left',
        align: 'left',
        width: 100,
        type: 'number',
        hideable: true,
        resizable: false,
        valueFormatter: ctValueFormatter,
        renderCell: ctFormatter,
      },
      {
        field: 'creditor_max',
        headerName: 'Creditors',
        headerAlign: 'left',
        align: 'left',
        width: 90,
        type: 'number',
        hide: true,
        hideable: true,
        sortable: false,
        resizable: false,
        valueFormatter: rangeValueFormatter('creditor_min', 'see petition'),
        renderCell: rangeFormatter('creditor_min', 'see petition'),
      },
      {
        field: 'assets_max',
        headerName: 'Assets',
        headerAlign: 'left',
        align: 'left',
        width: 120,
        type: 'number',
        hideable: true,
        sortable: false,
        resizable: false,
        valueFormatter: rangeValueFormatterKMB('assets_min', 'see petition'),
        renderCell: rangeFormatterKMB('assets_min', 'see petition'),
      },
      {
        field: 'liabilities_max',
        headerName: 'Liabilities',
        headerAlign: 'left',
        align: 'left',
        width: 120,
        type: 'number',
        hideable: true,
        sortable: false,
        resizable: false,
        valueFormatter: rangeValueFormatterKMB(
          'liabilities_min',
          'see petition'
        ),
        renderCell: rangeFormatterKMB('liabilities_min', 'see petition'),
      },
      {
        field: 'Actions',
        type: 'actions',
        width: 80,
        hideable: true,
        hideSortIcons: true,
        disableExport: true,
        disableReorder: true,
        sortable: false,
        filterable: false,
        groupable: false,
        getActions,
      },
    ],
    [
      isSummary,
      dateFormatter,
      linkFormatter,
      industryValueFormatter,
      industryFormatter,
      naValueFormatter,
      naFormatter,
      ctValueFormatter,
      ctFormatter,
      rangeValueFormatter,
      rangeFormatter,
      rangeValueFormatterKMB,
      rangeFormatterKMB,
      getActions,
    ]
  );

  const [cvm, setCvm] = useState<GridColumnVisibilityModel>({
    date_added: true,
    date_filed: false,
    case_name: true,
    case_number: false,
    industry: isSummary,
    city: isSummary,
    state_code: true,
    cs_chapter: true,
    creditor_max: true,
    assets_max: true,
    liabilities_max: true,
    Actions: true,
  });

  const onColumnVisibilityModelChange = useCallback(
    (newCvm: GridColumnVisibilityModel) => {
      setCvm({
        ...newCvm,
        //date_added: true,
        case_name: true,
        Actions: true,
      });
    },
    [setCvm]
  );

  const [pageSize, setPageSize] = useState(50);
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState(filters.search);

  const [sortModel, setSortModel] = useState<GridSortModel>([
    {
      field: 'date_added',
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
  const sorting = sortModel[0] as BankruptcySorting;

  // NOTE: disabled the 'using hooks in conditionals' warning because
  //       the isWatchlist never changes once the component is created
  const { data, isLoading: rowsLoading } = isWatchlist
    ? // eslint-disable-next-line react-hooks/rules-of-hooks
      useGetBankruptciesWatchlist(
        page + 1,
        itemsPerPage,
        filters,
        sorting,
        debouncedSearch || undefined
      )
    : // eslint-disable-next-line react-hooks/rules-of-hooks
      useGetBankruptcies(
        page + 1,
        itemsPerPage,
        filters,
        industriesFilter,
        sorting,
        debouncedSearch || undefined
      );

  const { data: industries, isLoading: industriesLoading } = useGetIndustries();

  const { data: restData, isLoading: restDataLoading } = useGetBankruptcies(
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
        getRowId={(r) => r.dci_id}
        getRowClassName={(params) => (params.row.isRest ? 'rest-row' : '')}
        hideFooter={isSummary}
        rowCount={count}
        pageSize={itemsPerPage}
        onPageSizeChange={isSummary ? undefined : setPageSize}
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
            header: isSummary ? { text: 'Corporate Bankruptcies' } : undefined,
            search: isSummary
              ? undefined
              : {
                  search,
                  setSearch,
                  placeholder: 'Bankruptcy Search…',
                },
            export: isSummary
              ? undefined
              : {
                  csvOptions: {
                    allColumns: true,
                  },
                },
            caption: isWatchlist
              ? {
                  text: 'BKwire continues monitoring your selected cases for missing impacted companies.',
                }
              : !isSummary
              ? {
                  text: 'Bankruptcy is a legal proceeding initiated when business is unable to repay outstanding debts or obligation',
                }
              : undefined,
          },
        }}
      />
      <Share ref={shareModal} />
    </>
  );
};
