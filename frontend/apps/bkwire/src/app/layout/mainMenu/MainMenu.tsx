import React from 'react';
import TrendingDownOutlined from '@mui/icons-material/TrendingDownOutlined';
import HomeIcon from '@mui/icons-material/Home';
import ListAlt from '@mui/icons-material/ListAlt';
import { Button, IconButton, useMediaQuery, useTheme } from '@mui/material';
import { Link, To } from 'react-router-dom';
import { useRouteUtils } from '../../hooks/useRouteUtils';
import { useHelpWizard } from '../../providers/HelpWizardProvider';
import { MainMenuRoot } from './MainMenu.styled';

const MainMenuNavLink = ({
  label,
  icon,
  to,
  area,
  page,
  setElement,
}: {
  label: string;
  icon: React.ReactNode;
  to: To;
  area: string;
  page?: string;
  setElement: React.Dispatch<React.SetStateAction<Element | null>>;
}) => {
  const theme = useTheme();
  const { matchArea, matchPage } = useRouteUtils();
  const mdScreen = useMediaQuery(
    theme.breakpoints.up(theme.breakpoints.values.md)
  );

  const className =
    matchArea(area) && (!page || matchPage(page)) ? 'active' : '';

  return mdScreen ? (
    <Button
      ref={setElement}
      component={Link}
      to={to}
      color="inherit"
      sx={{ lineHeight: 1, textAlign: 'center' }}
      className={className}
      startIcon={icon}
    >
      {label}
    </Button>
  ) : (
    <IconButton
      ref={setElement}
      component={Link}
      to={to}
      color="inherit"
      size="large"
      className={className}
      sx={{ p: '6px' }}
    >
      {icon}
    </IconButton>
  );
};

export const MainMenu = () => {
  const {
    setHomeElement,
    setAllBksElement,
    setAllLossesElement,
    setWatchlistElement,
  } = useHelpWizard();

  return (
    <MainMenuRoot>
      <MainMenuNavLink
        setElement={setHomeElement}
        to="/dashboard"
        area="dashboard"
        label="Dashboard"
        icon={<HomeIcon />}
      />
      <MainMenuNavLink
        setElement={setAllBksElement}
        to="/list/bankruptcies"
        area="list"
        page="bankruptcies"
        label="Corporate Bankruptcies"
        icon={<TrendingDownOutlined />}
      />
      <MainMenuNavLink
        setElement={setAllLossesElement}
        to="/list/losses"
        area="list"
        page="losses"
        label="Impacted Businesses"
        icon={<TrendingDownOutlined />}
      />
      <MainMenuNavLink
        setElement={setWatchlistElement}
        to="/watchlist/companies"
        area="watchlist"
        label="My watchlist"
        icon={<ListAlt />}
      />
    </MainMenuRoot>
  );
};
