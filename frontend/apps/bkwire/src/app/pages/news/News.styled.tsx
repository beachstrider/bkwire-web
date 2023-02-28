import { Box, List, styled } from '@mui/material';

export const NewsRoot = styled(Box)`
  padding: ${(p) => p.theme.spacing(0, 2)};
  cursor: pointer;

  &:hover {
    background-color: ${(p) => p.theme.palette.grey[100]};
  }

  &:last-of-type {
    .news-content {
      border-bottom: none;
    }
  }

  .news-content {
    padding: ${(p) => p.theme.spacing(2, 0)};
    display: flex;
    border-bottom: 1px solid ${(p) => p.theme.palette.grey[300]};

    .news-icon {
      display: flex;
      flex-shrink: 0;
      width: 32px;
      transform: translateY(-2px);

      svg {
        font-size: 18px;
        color: ${(p) => p.theme.palette.grey[700]};
      }
    }

    .news-body {
      flex-grow: 1;
    }

    .news-actions {
      flex-shrink: 0;
      width: 40px;
      text-align: right;
    }
  }
`;

export const NewsFilters = styled(List)`
  padding: 0;
  border-top: 1px solid ${(p) => p.theme.palette.grey[300]};

  .MuiSvgIcon-root {
    margin-right: ${(p) => p.theme.spacing(2)};
  }

  .MuiListItemButton-root {
    &.Mui-selected {
      .MuiTypography-root {
        font-weight: bold;
      }
    }
  }
`;
