import { styled } from '@mui/material';
import { ButtonLink } from '../../components/ButtonLink';
import { PagePaper } from '../../components/PagePaper.styled';

export const GridSummaryPaper = styled(PagePaper)`
  display: flex;
  flex-direction: column;
  margin-bottom: ${(p) => p.theme.spacing(3)};
  height: 734px;

  .MuiDataGrid-root {
    top: 1px;
  }

  .view-all {
    display: flex;
    justify-content: center;
    align-content: center;
    padding: ${(p) => p.theme.spacing(1)};
    background: ${(p) => p.theme.palette.grey[200]};
    z-index: 1;
  }
`;

export const NewsItem = styled(ButtonLink)`
  display: inline-block;
  text-align: left;
  border-bottom: 1px solid ${(p) => p.theme.palette.grey[200]};
  border-radius: 0;
  padding: ${(p) => p.theme.spacing(1, 0)};
  line-height: 23px;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;

  &:last-of-type {
    border-bottom: none;
  }
`;
