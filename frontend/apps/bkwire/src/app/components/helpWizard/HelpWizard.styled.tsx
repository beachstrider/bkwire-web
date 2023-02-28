import { Box, Dialog, Popover, PopoverOrigin, styled } from '@mui/material';
import wizardHeader from '../../../assets/wizard-header.jpg';
import { nonAttr } from '../../utils/styled';

export const WizardIntro = styled(Dialog)`
  .MuiDialog-paper {
    background-color: black;
    color: white;
  }

  .MuiDialogActions-root {
    padding: ${(p) => p.theme.spacing(2)};

    .MuiButton-root {
      min-width: 140px;
    }
  }

  .modal-header {
    height: 180px;
    background-color: white;
    background: url(${wizardHeader});
    padding: ${(p) => p.theme.spacing(2)};
  }

  .modal-body {
    height: 180px;
    padding: ${(p) => p.theme.spacing(2)};

    .MuiTypography-body3 {
      color: ${(p) => p.theme.palette.grey[500]};
    }

    .MuiTypography-body2 {
      color: ${(p) => p.theme.palette.grey[400]};
    }
  }

  .modal-close {
    position: absolute;
    right: 4px;
    top: 4px;
    color: black;
  }
`;

export const WizardStep = styled(Popover)`
  .MuiPaper-root {
    width: 400px;
    min-height: 160px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: visible;
    padding: ${(p) => p.theme.spacing(2)};
    background-color: black;
    color: white;
    transition: left 140ms ease-in-out, right 140ms ease-in-out,
      top 140ms ease-in-out, bottom 140ms ease-in-out,
      transform 140ms ease-in-out, opacity 210ms ease-in-out !important;

    .close-btn {
      align-self: start;
      padding: 0;
      margin-left: 10px;
    }

    .step-index {
      margin-bottom: -5px;
    }
  }
`;

export const PopoverArrow = styled(Box, nonAttr('origin'))<{
  origin: PopoverOrigin | undefined;
}>`
  position: absolute;

  ${(p) => p.origin?.vertical || 'top'}: 0;
  ${(p) => p.origin?.horizontal || 'left'}: ${(p) => p.theme.spacing(3)};

  &::before {
    background-color: black;
    content: '';
    display: block;
    position: absolute;
    width: 10px;
    height: 10px;
    top: -5px;
    transform: rotate(45deg);
    left: calc(50% - 6px);
  }
`;
