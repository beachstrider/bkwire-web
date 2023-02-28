import { Check } from '@mui/icons-material';
import { Typography } from '@mui/material';
import React from 'react';
import { SelectMatrixItemRoot } from './SelectMatrix.styled';
import { SelectMatrixItemProps } from './SelectMatrix.types';

export const SelectMatrixItem: React.FC<SelectMatrixItemProps> = ({
  text,
  icon,
  selected,
  onToggle,
}) => (
  <SelectMatrixItemRoot selected={selected} onClick={onToggle}>
    {icon}
    <Check />
    <Typography variant="body2">{text}</Typography>
  </SelectMatrixItemRoot>
);

export default SelectMatrixItem;
