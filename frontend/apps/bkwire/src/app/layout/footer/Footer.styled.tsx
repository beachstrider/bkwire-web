import { Box, styled } from '@mui/material';
import logo from '../../../assets/bkwirelogo.png';

export const FooterRoot = styled(Box)`
  display: flex;
  align-items: center;
  background-color: ${(p) => p.theme.palette.grey[300]};

  .MuiContainer-root {
    display: flex;
    justify-content: center;
  }

  .logo {
    border: 1px solid ${(p) => p.theme.palette.grey[300]};
    width: 305px;
    height: 100%;
    justify-content: center;
    align-items: center;
    display: flex;
    background-size: 100% !important;
    background-repeat: no-repeat !important;
    margin-right: ${(p) => p.theme.spacing(6)};
    background: url('${logo}');
  }

  .links-col {
    flex-grow: 1;

    .link {
      display: block;
      color: ${(p) => p.theme.palette.brand.main};
      font-size: 0.875rem;
      text-decoration: none;
      margin: ${(p) => p.theme.spacing(1, 0)};

      &:hover {
        text-decoration: underline;
      }

      .MuiSvgIcon-root {
        font-size: 18px;
        transform: translateY(4px);
        margin-right: ${(p) => p.theme.spacing(1)};
      }

      &.disabled {
        color: ${(p) => p.theme.palette.grey[500]};
      }
    }
  }

  .copyright {
    color: ${(p) => p.theme.palette.grey['500']};
    text-align: center;
    padding: ${(p) => p.theme.spacing(2, 0)};
  }
`;
