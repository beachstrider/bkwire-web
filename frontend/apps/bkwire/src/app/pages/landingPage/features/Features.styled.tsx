import { Box, styled } from '@mui/material';
import { PagePaper } from '../../../components/PagePaper.styled';
import { nonAttr, vignetteCss } from '../../../utils/styled';

export const FeaturesRoot = styled(PagePaper)`
  display: flex;
  flex-direction: column;
  padding: ${(p) => p.theme.spacing(5)};

  & > div:nth-of-type(even) {
    flex-direction: row-reverse;

    .text {
      text-align: right;
      padding-left: ${(p) => p.theme.spacing(4)};
      padding-right: 0;
    }
  }
`;

export const Feature = styled(Box, nonAttr('imgSrc'))<{ imgSrc: string }>`
  display: flex;
  padding: ${(p) => p.theme.spacing(5)};

  .text {
    width: 50%;
    padding-right: ${(p) => p.theme.spacing(4)};

    h1 {
      font-weight: bold;
      margin-bottom: ${(p) => p.theme.spacing(1)};
    }
  }

  .image {
    width: 50%;
    height: 240px;
    background: url(${(p) => p.imgSrc});
    background-position: center;
    background-size: cover;
    position: relative;
    box-shadow: ${(p) => p.theme.shadows[4]};

    ${vignetteCss(100, 0.7)}
  }
`;
