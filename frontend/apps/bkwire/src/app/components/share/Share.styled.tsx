import { Dialog, styled } from '@mui/material';

export const ShareRoot = styled(Dialog)`
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
    height: 160px;
    background-color: white;
    padding: ${(p) => p.theme.spacing(6, 8, 0, 8)};

    .MuiTabs-root {
      width: 100%;

      .MuiTab-root {
        flex-grow: 1;
      }
    }
  }

  .modal-body {
    padding: ${(p) => p.theme.spacing(6, 8, 6, 8)};

    .modal-body-panel {
      width: 100%;

      .MuiFormControl-root {
        width: 100%;

        .MuiInputBase-root {
          background-color: white;
        }

        margin-top: ${(p) => p.theme.spacing(1)};
      }

      .MuiDialogActions-root {
        padding: 0;
        margin-top: ${(p) => p.theme.spacing(2)};

        .MuiButton-root {
          width: 100%;
        }
      }
    }
  }

  .modal-close {
    position: absolute;
    right: 4px;
    top: 4px;
    color: ${(p) => p.theme.palette.grey[400]};
  }
`;
