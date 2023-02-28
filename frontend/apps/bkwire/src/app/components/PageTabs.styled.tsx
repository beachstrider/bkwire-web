import { styled, Tabs } from '@mui/material';

export const PageTabs = styled(Tabs)`
  position: relative;
  margin-bottom: ${(p) => p.theme.spacing(2)};
  max-width: 100%;
  height: ${(p) => p.theme.layout.pageTabsHeight}px;

  &::before {
    content: '';
    position: absolute;
    width: 100%;
    bottom: 0;
    left: 0;
    border-bottom: 1px solid ${(p) => p.theme.palette.grey[400]};
  }

  .MuiTab-root {
    background-color: ${(p) => p.theme.palette.grey[300]};
    border: 1px solid ${(p) => p.theme.palette.grey[300]};
    border-bottom: 1px solid ${(p) => p.theme.palette.grey[400]};

    &.Mui-selected {
      background-color: ${(p) => p.theme.palette.grey[100]};
      border: 1px solid ${(p) => p.theme.palette.grey[400]};
      border-bottom: 1px solid ${(p) => p.theme.palette.grey[100]};
    }
  }

  .MuiTabs-indicator {
    top: 0;
  }
`;
