import { Box, styled } from '@mui/material';

export const PagePaper = styled(Box)`
  background-color: white;
  box-shadow: ${(p) => p.theme.pagePaperShadow};
`;
