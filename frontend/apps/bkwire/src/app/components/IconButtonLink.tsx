import { IconButton, IconButtonProps, styled } from '@mui/material';
import { Link } from 'react-router-dom';

export const IconButtonLink = styled(
  <C extends React.ElementType>(props: IconButtonProps<C, { to?: string }>) => (
    <IconButton component={props.to ? Link : 'button'} {...props} to={props.to}>
      {props.children}
    </IconButton>
  )
)``;
