import { Box, styled } from '@mui/material';

export const ConceptRoot = styled(Box)`
  display: flex;
  flex-direction: column;
  width: 600px;
  align-self: center;
  padding: ${(p) => p.theme.spacing(6)};

  & > h1 {
    font-weight: bold;
    text-align: center;
  }

  .step {
    display: flex;
    gap: ${(p) => p.theme.spacing(5)};
    padding: ${(p) => p.theme.spacing(4, 0)};

    .step-nr {
      display: flex;
      justify-content: center;
      align-items: center;
      width: 180px;
      height: 80px;
      border: 2px solid ${(p) => p.theme.palette.grey[400]};
      border-radius: 26px;

      h1 {
        color: ${(p) => p.theme.palette.grey[400]};
      }
    }
    .step-details {
      h2 {
        font-weight: bold;
        padding: ${(p) => p.theme.spacing(1, 0)};
      }
    }
  }

  .MuiButton-root {
    width: 235px;
    align-self: center;
    margin: ${(p) => p.theme.spacing(2, 0)};
  }
`;
