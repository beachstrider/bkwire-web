import { Dialog, styled } from '@mui/material';

export const VideoPopupRoot = styled(Dialog)`
  .MuiDialog-paper {
    width: 960px;
    max-width: 960px;
    background-color: black;
    color: white;
  }

  .modal-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;

    .MuiTypography-h2 {
      color: white;
    }
  }

  .modal-body {
    background-color: white;
  }

  .modal-close {
    position: absolute;
    right: 4px;
    top: 4px;
    color: ${(p) => p.theme.palette.grey[400]};
  }
`;
