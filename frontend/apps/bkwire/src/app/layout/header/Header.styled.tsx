import { AppBar, Box, css, styled } from '@mui/material';
import { nonAttr } from '../../utils/styled';

export const headerGlobalStyles = (headerHeight: number) => css`
  .app {
    padding-top: ${headerHeight}px;
  }
`;

export const HeaderRoot = styled(AppBar, nonAttr('height', 'inverted'))<{
  height: number;
  inverted: boolean;
}>`
  background: ${(p) =>
    p.inverted
      ? 'white'
      : `linear-gradient(to right, black, black, ${p.theme.palette.brand.main})`};
  color: ${(p) => (p.inverted ? 'black' : 'white')};
  border-bottom: 1px solid
    ${(p) => (p.inverted ? p.theme.palette.grey[300] : 'white')};

  .MuiToolbar-root {
    height: ${(p) => p.height}px;
  }

  .bk-logo {
    filter: brightness(${(p) => (p.inverted ? 0 : 1)});
  }
`;

export const TrialBadgeRoot = styled(Box)`
  position: absolute;
  top: 64px;
  right: 0;
  z-index: -1;

  .MuiButton-root {
    border-radius: 0;
    padding: 0 20px;
    min-width: 118px;
  }
`;
