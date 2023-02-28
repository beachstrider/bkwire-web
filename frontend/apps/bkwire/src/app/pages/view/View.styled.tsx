import { Box, styled } from '@mui/material';
import { PagePaper } from '../../components/PagePaper.styled';
import { nonAttr } from '../../utils/styled';

export const InfoBoxRoot = styled(PagePaper)`
  display: flex;
  flex-direction: column;
  min-height: 153px;

  .info-box-header {
    display: flex;
    align-items: start;
    justify-content: space-between;
    padding: ${(p) => p.theme.spacing(2, 2, '2px', 2)};

    .MuiSvgIcon-root {
      color: ${(p) => p.theme.palette.grey[400]};
    }
  }
`;

export const InfoBoxContentRoot = styled(Box, nonAttr('width'))<{
  width: string | undefined;
}>`
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  justify-content: center;
  padding: ${(p) => p.theme.spacing(0, 2, 0, 2)};

  width: ${(p) => (p.width ? p.width : 'unset')};

  .info-box-label {
    position: relative;
    height: ${(p) => p.theme.typography.body2.minHeight}px;
    width: max-content;

    .info-box-label-adornment {
      position: absolute;
      top: 0;
      right: ${(p) => p.theme.spacing(-3)};
      cursor: pointer;

      .MuiSvgIcon-root {
        font-size: ${(p) => p.theme.typography.body1.fontSize};
      }
    }
  }

  .MuiTypography-root {
    margin: 0;
  }

  .MuiTypography-body2 {
    font-weight: 500;
  }

  .MuiTypography-h1 {
    font-weight: 300;
  }

  .MuiTypography-caption {
  }
`;

export const ContactCard = styled(Box)`
  display: flex;
  flex-direction: column;
  flex: 1;
  margin-top: ${(p) => p.theme.spacing(1.5)};
  padding: ${(p) => p.theme.spacing(2)};
  border-top: 1px solid ${(p) => p.theme.palette.grey[300]};
  border-right: 1px solid ${(p) => p.theme.palette.grey[300]};

  &:last-of-type {
    border-right: none;
  }

  .contact-card-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: ${(p) => p.theme.spacing(3)};

    .MuiIconButton-root {
      padding: 0;
    }

    .MuiSvgIcon-root {
      font-size: 18px;
    }
  }

  .contact-card-content {
    .MuiTypography-root {
      line-height: 1.4rem;
    }
  }
`;

export const Form201Icon = styled(PagePaper, nonAttr('imgSrc'))<{
  imgSrc: string;
}>`
  display: flex;
  justify-content: center;
  align-items: center;
  background-image: url('${(p) => p.imgSrc}');
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
  cursor: pointer;

  .hint {
    flex-direction: column;
    gap: ${(p) => p.theme.spacing(2)};
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.8);
    box-shadow: ${(p) => p.theme.shadows[4]} !important;
    display: none;
  }

  &:hover {
    .hint {
      display: flex;
    }
  }
`;

export const TabBox = styled(PagePaper)`
  display: flex;
  flex-direction: column;
  padding: 0;
  min-height: 491px;

  .MuiTabs-root,
  .MuiTab-root {
    min-height: 52px;
  }

  .MuiTab-root {
    font-size: ${(p) => p.theme.typography.h2.fontSize};
  }
`;

export const ActivityGridRoot = styled(Box)`
  display: flex;
  width: 100%;
  height: 100%;

  .MuiDataGrid-row {
    min-height: 110px !important;
    max-height: unset !important;
    height: unset !important;
  }

  .MuiDataGrid-cell {
    align-items: start !important;
    padding: ${(p) => p.theme.spacing(1, 1.25)} !important;
    min-height: unset !important;
    max-height: unset !important;
    height: unset !important;
    white-space: normal !important;
  }
`;
