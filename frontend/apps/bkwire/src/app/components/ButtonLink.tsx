import { Button, ButtonProps, styled } from '@mui/material';
import { Link } from 'react-router-dom';
import { nonAttr } from '../utils/styled';
import { Loading } from './loading/Loading';

const ButtonLinkRoot = styled(Button, nonAttr('minWidth', 'minHeight'))<{
  minWidth?: number;
  minHeight?: number;
}>`
  ${(p) => (p.minWidth !== undefined ? `min-width: ${p.minWidth}px;` : '')}
  ${(p) => (p.minHeight !== undefined ? `min-height: ${p.minHeight}px;` : '')}
`;

export const ButtonLink = <C extends React.ElementType>(
  props: ButtonProps<
    C,
    { to?: string; isLoading?: boolean; minWidth?: number; minHeight?: number }
  >
) => {
  const { minWidth, minHeight, isLoading: loading, ...restProps } = props;

  return (
    <ButtonLinkRoot
      variant="link"
      component={props.to ? Link : 'button'}
      {...restProps}
      to={props.to}
      minWidth={minWidth}
      minHeight={minHeight}
    >
      {loading ? <Loading size={20} color="inherit" /> : props.children}
    </ButtonLinkRoot>
  );
};
