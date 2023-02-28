import { Box, styled } from '@mui/material';
import logo from '../../../assets/bklogo.png';

export const LogoRoot = styled(Box)`
  .MuiButton-root {
    flex-shrink: 0;
    width: 87px;
    height: 58px;
    color: inherit;
    font-size: 2.125rem;
    text-decoration: none;
    background: url('${logo}');
  }
`;
