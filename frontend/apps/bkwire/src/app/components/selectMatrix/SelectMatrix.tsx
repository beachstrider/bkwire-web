import React, { useCallback } from 'react';
import { SelectMatrixRoot } from './SelectMatrix.styled';
import { SelectMatrixProps } from './SelectMatrix.types';
import { SelectMatrixItem } from './SelectMatrixItem';
import _includes from 'lodash/includes';

export const SelectMatrix: React.FC<SelectMatrixProps> = ({
  options,
  selected,
  setSelected,
  columns = 3,
}) => {
  const onToggle = useCallback(
    (value: number) => () =>
      setSelected((prevSelected) =>
        prevSelected.indexOf(value) !== -1
          ? prevSelected.filter((v) => v !== value)
          : [...prevSelected, value]
      ),
    [setSelected]
  );

  return (
    <SelectMatrixRoot columns={columns}>
      {options &&
        options.map(({ value, text, icon }) => (
          <SelectMatrixItem
            key={value}
            value={value}
            text={text}
            icon={icon}
            selected={_includes(selected, value)}
            onToggle={onToggle(value)}
          />
        ))}
    </SelectMatrixRoot>
  );
};
