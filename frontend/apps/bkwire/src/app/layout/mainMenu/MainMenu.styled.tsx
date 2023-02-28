import { Box, styled } from '@mui/material';

export const MainMenuRoot = styled(Box)`
  display: flex;
  flex-wrap: nowrap;
  color: ${(p) => p.theme.palette.grey['400']};

  .active {
    color: white;
    text-shadow: ${(p) => p.theme.textHighlightShadow};
  }
`;
