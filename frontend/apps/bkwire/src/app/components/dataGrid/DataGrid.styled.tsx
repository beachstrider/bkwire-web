import { Box, Button, css, styled, Theme } from '@mui/material';
import { GridToolbarColumnsButton, GridToolbarExport } from '@mui/x-data-grid';

export const ToolbarSearchInput = styled(Box)`
  display: flex;
  flex-direction: row;
  flex-grow: 1;
  padding: 0;
  margin-right: 10px;

  .MuiInputBase-root {
    flex-grow: 1;
  }

  .search-icon {
    margin: ${(p) => p.theme.spacing(1.8)};
  }

  .clear-icon {
    height: 30px;
    align-self: center;
  }
`;

const ToolbarButton = (theme: Theme) => css`
  height: 30px;
  min-width: 30px;
  align-self: center;
  margin-right: ${theme.spacing(1)};
`;

export const ToolbarExport = styled(GridToolbarExport)`
  ${(p) => ToolbarButton(p.theme)}
`;
export const ToolbarColumns = styled(GridToolbarColumnsButton)`
  ${(p) => ToolbarButton(p.theme)}
`;

export const ToolbarRefreshActivitiesButton = styled(Button)`
  height: 30px;
  margin-right: ${(p) => p.theme.spacing(1)};
  align-self: center;
`;
