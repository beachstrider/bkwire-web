import { useState } from 'react';
import {
  Checkbox,
  ListItem,
  ListItemButton,
  ListItemIcon,
  Typography,
} from '@mui/material';
import { FilterListRoot } from './Filters.styled';
import { ButtonLink } from '../../../components/ButtonLink';

export interface FilterListItem {
  id: number;
  name: string;
}

interface FilterListProps {
  items?: FilterListItem[];
  value: number[];
  onChange: (id: number) => () => void;
  visibleItemCount?: number;
  idPrefix?: string;
  children?: React.ReactNode;
}
export const FilterList = ({
  items,
  value,
  onChange,
  visibleItemCount = 5,
  idPrefix = 'item',
  children,
}: FilterListProps) => {
  const [showMore, setShowMore] = useState(false);

  const toListItem = (item: FilterListItem) => (
    <ListItem key={item.id}>
      <ListItemButton dense onClick={onChange(item.id)}>
        <ListItemIcon>
          <Checkbox size="small" checked={value.indexOf(item.id) !== -1} />
        </ListItemIcon>
        <Typography variant="body2" id={`${idPrefix}-${item.id}`}>
          {item.name}
        </Typography>
      </ListItemButton>
    </ListItem>
  );

  return (
    <FilterListRoot>
      {!!items && (
        <>
          {items.slice(0, visibleItemCount).map(toListItem)}

          {items.length > visibleItemCount &&
            showMore &&
            items.slice(visibleItemCount).map(toListItem)}

          {items.length > visibleItemCount && (
            <ButtonLink
              onClick={() => setShowMore((prevShowMore) => !prevShowMore)}
            >
              {showMore ? 'Less options' : 'More options'}
            </ButtonLink>
          )}
        </>
      )}
      {children}
    </FilterListRoot>
  );
};
