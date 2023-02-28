import { Box, styled } from '@mui/material';
import { nonAttr } from '../utils/styled';

export interface PageGridProps {
  columns: number;
}
export const PageGrid = styled(Box, nonAttr('columns'))<PageGridProps>`
  display: grid;
  grid-template-columns: repeat(${(p) => p.columns}, 1fr);
  column-gap: ${(p) => p.theme.spacing(3)};
  row-gap: ${(p) => p.theme.spacing(2)};
  margin-bottom: ${(p) => p.theme.spacing(2)};
`;
