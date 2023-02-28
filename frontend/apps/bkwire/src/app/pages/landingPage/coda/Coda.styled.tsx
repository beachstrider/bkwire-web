import { Box, styled } from '@mui/material';

export const CodaRoot = styled(Box)`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: ${(p) => p.theme.spacing(10, 0, 12, 0)};

  h2 {
    font-weight: bold;
    margin: ${(p) => p.theme.spacing(2, 0, 3, 0)};
  }

  .MuiButton-root {
    width: 235px;
  }
`;
