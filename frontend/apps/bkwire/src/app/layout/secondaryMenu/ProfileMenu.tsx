import {
  Button,
  Divider,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import React from 'react';
import { MenuTabPanel, UserAvatar, UserHeader } from './SecondaryMenu.styled';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { useAuth0 } from '@auth0/auth0-react';
import { getInitials } from '../../utils/string';
import { Link } from 'react-router-dom';
import { useGetViewer } from '../../api/api.hooks';

interface ProfileMenuProps {
  close: () => void;
}
export const ProfileMenu: React.FC<ProfileMenuProps> = ({ close }) => {
  const { data: viewer } = useGetViewer();
  const { user, logout } = useAuth0();

  const fullName = viewer
    ? `${viewer.first_name || ''} ${viewer.last_name || ''}`
    : user?.name || user?.email || '';

  return (
    <MenuTabPanel>
      <List component="div">
        <ListItem component="div">
          <UserAvatar>{getInitials(fullName)}</UserAvatar>
          <UserHeader>
            <div className="user-name">{fullName}</div>
            <Button
              variant="contained"
              color="info"
              size="large"
              onClick={close}
              component={Link}
              to="/account/profile"
            >
              View profile
            </Button>
          </UserHeader>
        </ListItem>
        <ListItemButton to="/account/billing" onClick={close} component={Link}>
          <ListItemText primary="Upgrade" />
          <ListItemIcon>
            <OpenInNewIcon fontSize="small" />
          </ListItemIcon>
        </ListItemButton>
        <Divider variant="middle" />
        <ListItemButton
          onClick={() => logout({ returnTo: window.location.origin })}
        >
          <ListItemText primary="Sign out" />
          <ListItemIcon>
            <ArrowForwardIcon fontSize="small" />
          </ListItemIcon>
        </ListItemButton>
      </List>
    </MenuTabPanel>
  );
};
