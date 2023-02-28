import { Box, styled } from '@mui/material';
import { nonAttr } from '../../utils/styled';

export const SelectMatrixRoot = styled(Box, nonAttr('columns'))<{
  columns: number;
}>`
  background-color: ${(p) => p.theme.palette.grey[300]};
  display: grid;
  grid-gap: 1px;
  grid-template-columns: repeat(${(p) => p.columns}, 1fr);
  width: 100%;
  border: 1px solid ${(p) => p.theme.palette.grey[300]};
`;

export const SelectMatrixItemRoot = styled(Box, nonAttr('selected'))<{
  selected: boolean;
}>`
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-items: center;
  text-align: center;
  padding: ${(p) => p.theme.spacing(2)};
  background-color: ${(p) => (p.selected ? 'black' : 'white')};
  color: ${(p) => (p.selected ? 'white' : 'black')};
  cursor: pointer;

  &:hover {
    background-color: ${(p) => p.theme.palette.grey[p.selected ? 900 : 200]};
  }

  .MuiSvgIcon-root {
    margin: ${(p) => p.theme.spacing(2)};
    font-size: 36px;

    &:last-of-type {
      font-size: 17px;
      display: ${(p) => (p.selected ? 'block' : 'none')};
      color: ${(p) => p.theme.palette.success.main};
      position: absolute;
      top: 0px;
      right: 0px;
    }
  }
`;
