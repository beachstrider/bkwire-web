import React, { useCallback, useState } from 'react';
import {
  Box,
  CircularProgress,
  IconButton,
  InputBase,
  Popover,
  Tooltip,
  Typography,
} from '@mui/material';
import {
  DataGrid as MUIDataGrid,
  DataGridProps,
  GridSortDirection,
  GridToolbarExportProps,
} from '@mui/x-data-grid';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import {
  ToolbarSearchInput,
  ToolbarExport,
  ToolbarColumns,
  ToolbarRefreshActivitiesButton,
} from './DataGrid.styled';
import { Refresh } from '@mui/icons-material';
import { useCaseRefresh, useGetViewer } from '../../api/api.hooks';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';

export interface GridToolbarSearchProps {
  search: string;
  setSearch: (value: string) => void;
  placeholder?: string;
}

export interface GridToolbarRefreshActivitiesProps {
  caseId: number;
}

export interface GridToolbarCaptionProps {
  text: string;
}

export interface GridToolbarProps {
  header: GridToolbarCaptionProps | null;
  search: GridToolbarSearchProps | null;
  export: GridToolbarExportProps | null;
  refreshActivities: GridToolbarRefreshActivitiesProps | null;
  caption: GridToolbarCaptionProps | null;
  hideColumnsMenu?: boolean;
}

const rowsPerPageOptions = [25, 50, 100];
const sortingOrder: GridSortDirection[] = ['desc', 'asc'];

const ToolbarSearch = ({
  search,
  setSearch,
  placeholder = 'Search…',
}: GridToolbarSearchProps) => (
  <ToolbarSearchInput>
    <SearchIcon className="search-icon" fontSize="small" />
    <InputBase
      value={search}
      onChange={(e) => setSearch(e.target.value)}
      placeholder={placeholder}
    />
    <IconButton
      title="Clear"
      size="small"
      className="clear-icon"
      style={{ visibility: search ? 'visible' : 'hidden' }}
      onClick={() => setSearch('')}
    >
      <ClearIcon fontSize="small" />
    </IconButton>
  </ToolbarSearchInput>
);

const ToolbarRefreshActivities = ({
  caseId,
}: GridToolbarRefreshActivitiesProps) => {
  const { data: viewer } = useGetViewer();
  const refreshCase = useCaseRefresh(caseId);
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(() => {
    setLoading(true);
    refreshCase().finally(() => setLoading(false));
  }, [refreshCase]);

  const btn = (
    <ToolbarRefreshActivitiesButton
      color="primary"
      startIcon={loading ? <CircularProgress size={16} /> : <Refresh />}
      size="small"
      onClick={refresh}
      disabled={loading}
    >
      Refresh
    </ToolbarRefreshActivitiesButton>
  );

  return (
    <Tooltip
      title={
        viewer?.subscription === 'mvp'
          ? `${viewer.case_refresh_max - viewer.case_refresh_count} remaining`
          : 'Need MVP access!'
      }
      placement="top"
      disableInteractive
      arrow
    >
      <Box display="flex">{btn}</Box>
    </Tooltip>
  );
};

const ToolbarHeader = ({ text }: GridToolbarCaptionProps) => (
  <Typography p={2} variant="h2" flexGrow={1}>
    {text}
  </Typography>
);

const ToolbarCaption = ({ text }: GridToolbarCaptionProps) => (
  <Typography p={2} pt={0} variant="body2">
    {text}
  </Typography>
);

export const GridToolbar = (props: GridToolbarProps) => {
  const { data: viewer } = useGetViewer();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  return (
    <Box display="flex" flexDirection="column">
      <Box display="flex">
        {props.header && <ToolbarHeader {...props.header} />}
        {props.search && <ToolbarSearch {...props.search} />}
        {props.refreshActivities && (
          <ToolbarRefreshActivities {...props.refreshActivities} />
        )}
        {!props.hideColumnsMenu && <ToolbarColumns />}
        {props.export && (
          <ToolbarExport
            {...props.export}
            onClickCapture={(e: React.SyntheticEvent) => {
              if (
                !viewer ||
                viewer.subscription === 'none' ||
                viewer.subscription === 'individual'
              ) {
                e.stopPropagation();
                navigate('/account/billing');
                enqueueSnackbar('Exporting requires a TEAM subscription!', {
                  variant: 'info',
                });
              }
            }}
          />
        )}
      </Box>
      {props.caption && <ToolbarCaption {...props.caption} />}
    </Box>
  );
};

export const DataGrid: React.FC<DataGridProps> = ({
  componentsProps,
  ...props
}) => {
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [value, setValue] = useState('');

  const handlePopoverOpen = (event: React.MouseEvent<HTMLElement>) => {
    const field = event.currentTarget.dataset.field;
    if (
      field &&
      field !== 'Actions' &&
      event.currentTarget.clientWidth + 10 < event.currentTarget.scrollWidth
    ) {
      setValue(event.currentTarget.innerText);
      setAnchorEl(event.currentTarget);
    }
  };

  const handlePopoverClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);

  return (
    <>
      <MUIDataGrid
        {...props}
        rowHeight={40}
        headerHeight={40}
        scrollbarSize={17}
        rowsPerPageOptions={rowsPerPageOptions}
        paginationMode="server"
        sortingMode="server"
        sortingOrder={sortingOrder}
        disableVirtualization
        disableSelectionOnClick={true}
        disableColumnFilter={true}
        componentsProps={{
          ...componentsProps,
          cell: {
            onMouseEnter: handlePopoverOpen,
            onMouseLeave: handlePopoverClose,
          },
        }}
      />
      <Popover
        sx={{
          pointerEvents: 'none',
        }}
        open={open}
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
        transformOrigin={{
          vertical: -2,
          horizontal: 'left',
        }}
        onClose={handlePopoverClose}
        disableRestoreFocus
      >
        <Typography p={1}>{value}</Typography>
      </Popover>
    </>
  );
};
