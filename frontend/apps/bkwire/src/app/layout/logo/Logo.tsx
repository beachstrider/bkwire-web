import { ButtonLink } from '../../components/ButtonLink';
import { LogoRoot } from './Logo.styled';

export const Logo = () => (
  <LogoRoot>
    <ButtonLink className="bk-logo" to="/dashboard"></ButtonLink>
  </LogoRoot>
);
