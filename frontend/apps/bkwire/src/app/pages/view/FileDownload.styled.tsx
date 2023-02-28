import { Box, Dialog, styled } from '@mui/material';
import { nonAttr } from '../../utils/styled';

export const FileDownloadRoot = styled(Dialog)`
  .MuiDialog-paper {
    width: 600px;
    background-color: ${(p) => p.theme.palette.grey[200]};
    color: black;
  }

  .modal-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
  }

  .modal-body {
    background-color: white;
    padding: ${(p) => p.theme.spacing(2)};
  }

  .modal-close {
    position: absolute;
    right: 4px;
    top: 4px;
    color: ${(p) => p.theme.palette.grey[400]};
  }

  table {
    text-align: left;
    vertical-align: middle;

    th,
    td {
      padding: ${(p) => p.theme.spacing(1, 4, 1, 0)};

      .loading-spinner {
        justify-content: end;
      }
    }

    th:last-of-type,
    td:last-of-type {
      width: 100px;
      text-align: right;
      padding: ${(p) => p.theme.spacing(1, 0)};
    }
  }

  .file-access {
    font-weight: bold;

    &.owned::after {
      content: 'owned';
      color: green;
    }
    &.not-owned::after {
      content: 'not owned';
      color: red;
    }
  }

  .modal-footer {
    padding: ${(p) => p.theme.spacing(1, 2)};
    text-align: right;
    font-size: 14px;
    color: ${(p) => p.theme.palette.primary.main};
    font-weight: bold;
  }
`;

export const FileDownloadLink = styled(Box, nonAttr('disabled'))<{
  disabled: boolean;
}>`
  color: ${(p) =>
    p.disabled ? p.theme.palette.grey[400] : p.theme.palette.link.main};
  text-overflow: ellipsis;
  width: 430px;
  overflow: hidden;
  white-space: nowrap;
  cursor: ${(p) => (p.disabled ? 'auto' : 'pointer')};

  &:hover {
    text-decoration: ${(p) => (p.disabled ? 'none' : 'underline')};
  }
`;
