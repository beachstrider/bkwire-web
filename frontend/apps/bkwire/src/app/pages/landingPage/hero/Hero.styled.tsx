import { styled } from '@mui/material';
import { PagePaper } from '../../../components/PagePaper.styled';
import { vignetteCss } from '../../../utils/styled';
import landingHero from '../../../../assets/landing-hero.jpg';

export const HeroRoot = styled(PagePaper)`
  display: flex;
  margin-top: ${(p) => p.theme.spacing(4)};

  .hero-caption {
    width: 50%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    padding: ${(p) => p.theme.spacing(0, 10)};

    h1 {
      font-weight: bold;
    }
  }

  .hero-image {
    flex-grow: 1;
    width: 50%;
    height: 420px;
    margin-top: 50px;
    margin-bottom: 50px;
    background: url(${landingHero});
    position: relative;
    box-shadow: ${(p) => p.theme.shadows[2]};

    ${vignetteCss(130, 0.6)}
  }

  .recent-unsecurred-creditors {
    display: flex;
    flex-direction: column;
    position: absolute;
    top: 50px;
    left: 40px;
    width: 300px;
    height: 400px;
    background: white;
    box-shadow: ${(p) => p.theme.shadows[3]};
    z-index: 1;

    .header {
      background: black;
      color: white;
      padding: ${(p) => p.theme.spacing(1.5, 2)};
    }

    .ruc {
      display: flex;
      padding: ${(p) => p.theme.spacing(1.2, 2)};
      border-bottom: 1px solid ${(p) => p.theme.palette.grey[300]};
    }

    .footer {
      width: 90%;
      justify-self: center;
      align-self: center;
      margin-top: ${(p) => p.theme.spacing(1)};
    }
  }
`;
