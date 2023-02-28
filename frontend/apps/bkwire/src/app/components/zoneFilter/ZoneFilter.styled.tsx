import { Box, Dialog, styled } from '@mui/material';

export const ZoneFilterRoot = styled(Box)`
  display: flex;
  gap: ${(p) => p.theme.spacing(1)};

  .MuiChip-root {
    max-width: 160px;
  }

  .MuiIconButton-root {
    background-color: ${(p) => p.theme.palette.grey[200]};

    &:hover {
      background-color: ${(p) => p.theme.palette.grey[300]};
    }
  }
`;

export const ZoneFilterDialog = styled(Dialog)`
  .MuiDialog-paper {
    border-radius: 0;
    max-width: 900px;
  }

  .MuiDialogActions-root {
    padding: ${(p) => p.theme.spacing(1, 2, 2, 2)};
  }
`;

export const ZoneFilterContainer = styled(Box)`
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: auto;

  -ms-overflow-style: none; /* for Internet Explorer, Edge */
  scrollbar-width: none; /* for Firefox */

  &::-webkit-scrollbar {
    display: none; /* for Chrome, Safari, and Opera */
  }
`;
