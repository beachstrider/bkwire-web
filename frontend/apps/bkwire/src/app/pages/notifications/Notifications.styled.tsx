import { Box, List, styled } from '@mui/material';

export const NotificationRoot = styled(Box)`
  padding: ${(p) => p.theme.spacing(0, 2)};
  cursor: pointer;

  &:hover {
    background-color: ${(p) => p.theme.palette.grey[100]};
  }

  &:last-of-type {
    .notif-content {
      border-bottom: none;
    }
  }

  .notif-content {
    padding: ${(p) => p.theme.spacing(1.25, 0)};
    display: flex;
    border-bottom: 1px solid ${(p) => p.theme.palette.grey[300]};

    .notif-status {
      display: flex;
      align-items: center;
      flex-shrink: 0;
      width: 16px;
      cursor: pointer;

      .MuiSvgIcon-root {
        font-size: 10px;
      }
    }

    .notif-icon {
      display: flex;
      align-items: center;
      flex-shrink: 0;
      width: 32px;
    }

    .notif-body {
      flex-grow: 1;

      .notif-title {
        cursor: pointer;

        &:hover: {
          text-decoration: underline;
        }
      }

      .notif-details {
        /* white-space: nowrap;
        text-overflow: ellipsis;
        width: 250px;
        overflow: hidden; */
      }
    }

    .notif-actions {
      flex-shrink: 0;
      width: 40px;
      text-align: right;
    }
  }
`;

export const NotificationFilters = styled(List)`
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
