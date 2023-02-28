import { Accordion, Box, List, styled } from '@mui/material';
import { PagePaper } from '../../../components/PagePaper.styled';

export const FiltersRoot = styled(PagePaper)`
  width: 240px;
  padding: 0;
  margin-right: ${(p) => p.theme.spacing(2)};
`;

export const FiltersHeader = styled(Box)`
  display: flex;
  justify-content: space-between;
  height: 48px;
  padding: ${(p) => p.theme.spacing(0, 2)};

  .MuiTypography-body2 {
    font-weight: bold;
    align-self: center;
  }
`;

export const FilterAccordion = styled(Accordion)`
  box-shadow: none;
  border-top: 1px solid ${(p) => p.theme.palette.grey[300]};

  .MuiAccordionSummary-root {
    min-height: 38px;

    .MuiAccordionSummary-content {
      margin: 0;

      .MuiTypography-body2 {
        font-weight: bold;
      }
    }

    .MuiAccordionSummary-expandIconWrapper {
      margin-right: -6px;
    }
  }

  .MuiAccordionDetails-root {
    padding: 0;
  }
  .MuiSlider-markLabel {
    font-size: 10px;
    color: ${(p) => p.theme.palette.grey[400]};
  }
`;

export const FilterListRoot = styled(List)`
  padding: ${(p) => p.theme.spacing(0, 0, 2, 0)};

  .MuiListItem-root {
    padding: 0;

    .MuiListItemButton-root {
      padding: ${(p) => p.theme.spacing(0.5, 1.7)};

      .MuiCheckbox-root {
        margin: 0;
        padding: 0;
      }

      .MuiListItemIcon-root {
        min-width: 30px;
      }
    }
  }
  .MuiButton-root {
    margin: ${(p) => p.theme.spacing(1, 2, 0, 2)};
  }
`;
