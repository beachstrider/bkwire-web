import { Box, styled } from '@mui/material';
import { PagePaper } from '../../../components/PagePaper.styled';
import { vignetteCss } from '../../../utils/styled';
import { nonAttr } from '../../../utils/styled';

export const PartnersRoot = styled(PagePaper)`
  padding: ${(p) => p.theme.spacing(8, 0)};

  & > div {
    position: relative;
    margin: ${(p) => p.theme.spacing(0, 20)};
  }
`;

export const PartnerCard = styled(Box, nonAttr('logo'))<{ logo: string }>`
  position: relative;
  border-radius: ${(p) => p.theme.spacing(0.5)};
  box-shadow: ${(p) => p.theme.shadows[3]};

  & > div {
    background: url(${(p) => p.logo});
    background-position: center;
    padding: 30px;
    height: 100%;

    ${vignetteCss(50, 0.2)};
  }
`;
