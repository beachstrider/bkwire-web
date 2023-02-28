import { Box, styled } from '@mui/material';
import { nonAttr } from '../../utils/styled';

export const OnboardingRoot = styled('div')`
  display: flex;
  flex-grow: 1;
  flex-direction: column;
  justify-content: center;
  justify-items: center;
  align-content: center;
  align-items: center;
  max-width: 650px;
  padding: ${(p) => p.theme.spacing(6, 0)};
  margin: auto;
`;

export const StepperRoot = styled('div')`
  display: flex;
  justify-content: center;
  flex-grow: 1;
  padding-right: ${(p) => p.theme.spacing(11)};

  .MuiStepper-root {
    width: 500px;

    .Mui-completed {
      color: ${(p) => p.theme.palette.success.dark};
    }
  }
`;

export const FormControl = styled(Box, nonAttr('inline'))<{ inline?: boolean }>`
  position: relative;
  width: 100%;
  padding: ${(p) => p.theme.spacing(!p.inline ? 2 : 1, 0, 1, 0)};

  &:first-of-type {
    padding: ${(p) => p.theme.spacing(1, 0, 1, 0)};

    .remove-btn {
      top: ${(p) => p.theme.spacing(2)};
    }
  }

  .MuiFormControl-root {
    width: 100%;
  }

  .remove-btn {
    position: absolute;
    top: ${(p) => p.theme.spacing(3)};
    left: ${(p) => p.theme.spacing(-4)};
    padding: ${(p) => p.theme.spacing(0.25)};

    svg {
      font-size: 1.2rem;
    }
  }
`;
