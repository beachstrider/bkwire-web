import { Box, css, styled } from '@mui/material';
import { nonAttr } from '../../utils/styled';

const noOutline = css`
  outline: none !important;
  border: none !important;
  border-radius: 0 !important;
`;

export const SearchRoot = styled(Box, nonAttr('showResults'))<{
  showResults: boolean;
}>`
  margin-right: ${(p) => p.theme.spacing(2)};

  .MuiAutocomplete-root {
    background: white;
    width: 164px;

    & * {
      ${noOutline}
      transition-duration: 0ms !important;
    }

    & .MuiFormControl-root {
      .MuiInputBase-root {
        padding: ${(p) => p.theme.spacing(0, 2)};
        font-size: 14px;

        .MuiSvgIcon-root {
          color: ${(p) => p.theme.palette.grey[500]};
        }
      }
    }

    &:hover {
      & .MuiFormControl-root {
        .MuiInputBase-root {
          .MuiSvgIcon-root {
            color: ${(p) => p.theme.palette.grey[800]};
          }
        }
      }
    }

    &.Mui-focused {
      width: 440px;

      & .MuiFormControl-root {
        .MuiInputBase-root {
          .MuiSvgIcon-root {
            color: ${(p) => p.theme.palette.grey[800]};
          }
        }
      }
    }
  }

  .MuiAutocomplete-popper {
    display: ${(p) => (p.showResults ? 'block' : 'none')};

    .MuiPaper-root {
      border-radius: 0;
      border-top: 1px solid ${(p) => p.theme.palette.grey[500]};
      margin-left: 0;
      margin-right: 0;

      .MuiAutocomplete-listbox {
        padding: 0;
        max-height: none;
      }
    }

    .MuiAutocomplete-option {
      padding-top: ${(p) => p.theme.spacing(1)};
      padding-bottom: ${(p) => p.theme.spacing(1)};
    }
  }
`;

export const SearchGroup = styled(Box)`
  border-top: 1px solid ${(p) => p.theme.palette.grey[300]};

  &:first-of-type {
    border-top: none;
  }

  .search-group-header {
    display: flex;
    justify-content: space-between;
    padding: ${(p) => p.theme.spacing(1, 2)};
    font-size: 12px;
    color: ${(p) => p.theme.palette.grey[500]};

    .MuiButton-link {
      font-size: 12px;
      height: 14px;
    }
  }

  .search-group-options {
    padding-bottom: ${(p) => p.theme.spacing(3)};
  }
`;

export const SearchOption = styled(Box)`
  display: flex;
  justify-content: space-between !important;
  padding-left: ${(p) => p.theme.spacing(4)} !important;
  font-size: 14px;
`;
