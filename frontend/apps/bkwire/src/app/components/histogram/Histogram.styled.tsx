import { Box, styled } from '@mui/material';
import { nonAttr } from '../../utils/styled';

export const HistogramRoot = styled(Box, nonAttr('yStepCount'))<{
  yStepCount: number;
}>`
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  overflow: hidden;
  height: 100%;
  padding: ${(p) => p.theme.spacing(2)};

  .top {
    display: flex;
    flex-grow: 1;

    .y-label {
      display: flex;
      width: 20px;
      height: 100%;
      position: relative;

      .MuiTypography-verticalLabel {
        position: absolute;
        left: -90px;
        width: 200px;
      }
    }
    .y-steps {
      display: flex;
      flex-direction: column;
      position: relative;

      .MuiTypography-body3 {
        flex-grow: 1;
        padding-left: ${(p) => p.theme.spacing(1)};
        padding-right: ${(p) => p.theme.spacing(1)};
        text-align: end;
        margin-top: -${(p) => p.theme.spacing(1)};
        color: ${(p) => p.theme.palette.grey[600]};

        &:last-child {
          position: absolute;
          bottom: -10px;
          right: 0;
        }
      }
    }

    .histogram {
      display: flex;
      align-items: end;
      flex-grow: 1;
      border-left: 1px solid ${(p) => p.theme.palette.grey[500]};
      border-bottom: 1px solid ${(p) => p.theme.palette.grey[500]};
      border-right: 1px solid ${(p) => p.theme.palette.grey[200]};

      background-size: 100% calc(100% / ${(p) => p.yStepCount - 1});
      background-image: linear-gradient(
        ${(p) => p.theme.palette.grey[200]} 1px,
        transparent 0px
      );
    }
  }

  .bottom {
    padding-top: ${(p) => p.theme.spacing(3)};

    .x-label {
      text-align: center;
    }
  }

  .legend {
    display: flex;
    align-items: center;
    color: ${(p) => p.theme.palette.grey[600]};

    &::before {
      display: inline-block;
      content: '';
      width: 15px;
      height: 15px;
      margin-top: -3px;
      margin-right: ${(p) => p.theme.spacing(1)};
      background-color: ${(p) => p.theme.palette.brand.main};
    }
  }
`;

export const HistogramColumn = styled(Box, nonAttr('emphasize'))<{
  emphasize: boolean;
}>`
  height: 100%;
  flex-grow: 1;
  display: flex;
  flex-direction: column-reverse;

  .h-column {
    position: relative;
    background-color: ${(p) => p.theme.palette.brand.main};
    margin-left: 1px;
    margin-right: 1px;

    .h-date {
      width: 100px;
      position: absolute;
      bottom: -${(p) => p.theme.spacing(3)};
      left: calc(50% - 50px);
      text-align: center;
      font-weight: ${(p) => (p.emphasize ? 'bold' : 'normal')};
      color: ${(p) => p.theme.palette.grey[p.emphasize ? 800 : 600]};
    }

    .h-count {
      width: 100px;
      position: absolute;
      top: -${(p) => p.theme.spacing(2)};
      left: calc(50% - 50px);
      text-align: center;
      font-weight: bold;
      color: ${(p) => p.theme.palette.brand.main};
      display: none;
    }
  }
  &:hover .h-column .h-count {
    display: block;
  }
`;
