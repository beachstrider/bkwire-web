import React from 'react';
import {
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import { MenuTabPanel } from './SecondaryMenu.styled';
import OndemandVideoIcon from '@mui/icons-material/OndemandVideo';
import { videos, VideoType } from './VideoPopup';

interface HelpMenuProps {
  close: () => void;
  openHelpWizard: () => void;
  openVideoPopup: (type: VideoType) => void;
}

export const HelpMenu: React.FC<HelpMenuProps> = ({ openVideoPopup }) => {
  return (
    <MenuTabPanel>
      <List component="div">
        <ListItem component="div">
          <ListItemText primary="Help" />
        </ListItem>
        {Object.keys(videos).map((type) => (
          <ListItemButton
            key={videos[type].title}
            onClick={() => openVideoPopup(type)}
          >
            <ListItemText primary={videos[type].title} />
            <ListItemIcon>
              <OndemandVideoIcon fontSize="small" />
            </ListItemIcon>
          </ListItemButton>
        ))}
        {/* <ListItemButton onClick={openHelpWizard}>
          <ListItemText primary="Product tour" />
          <ListItemIcon>
            <OpenInNewIcon fontSize="small" />
          </ListItemIcon>
        </ListItemButton> */}
      </List>
    </MenuTabPanel>
  );
};
