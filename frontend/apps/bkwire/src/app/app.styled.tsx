import { Box, Container, css, styled } from '@mui/material';

export const globalStyles = css`
  body {
    /* overflow-y: scroll !important; */
    table,
    thead,
    tbody,
    th,
    tr,
    td {
      border: none;
    }
  }
`;

export const AppRoot = styled(Box)`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  min-width: ${(p) => p.theme.breakpoints.values.md}px;
  background-color: ${(p) => p.theme.palette.grey[100]};
`;

export const AppContainer = styled(Container)`
  display: flex;
  flex-grow: 1;
`;
