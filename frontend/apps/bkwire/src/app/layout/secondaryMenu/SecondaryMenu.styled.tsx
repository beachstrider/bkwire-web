import { Box, Tabs, styled, Avatar } from '@mui/material';
import { nonAttr } from '../../utils/styled';

export const MenuTabs = styled(Tabs, nonAttr('noTransition'))<{
  noTransition?: boolean;
}>`
  button.MuiTab-root {
    min-width: 0;
    padding: ${(p) => p.theme.spacing(2.5, 1)};
    opacity: 1;

    &[disabled] {
      width: 0;
      padding: 0;
      margin: 0;
    }
  }

  .MuiTabs-indicator {
    background-color: white;
    height: 4px;

    transition-duration: ${(p) =>
      p.noTransition ? '0ms' : `${p.theme.transitions.duration.standard}ms`};
  }
`;

export const MenuTabPanel = styled(Box)`
  position: absolute;
  right: 0;
  width: 375px;
  background-color: white;
  color: black;
  border: 1px solid black;
  margin-top: 1px;

  &::after {
    content: '';
    position: absolute;
    top: -2px;
    left: 0;
    width: 101%;
    height: 1px;
    background-color: white;
  }

  .MuiList-root {
    padding: 0;
  }

  .MuiListItem-root {
    &:first-of-type {
      background-color: black;
      color: white;
      padding-top: ${(p) => p.theme.spacing(3)};
      padding-bottom: ${(p) => p.theme.spacing(3)};

      .MuiListItemText-root {
        margin: 0;
      }

      .MuiListItemSecondaryAction-root {
        top: 22px;
        transform: none;
      }
    }
    .MuiListItemIcon-root,
    .MuiIconButton-root {
      color: white;
    }
  }

  .MuiListItemIcon-root,
  .MuiIconButton-root {
    color: black;
    min-width: unset;
    padding: 0;
  }

  .MuiDivider-root {
    border-color: ${(p) => p.theme.palette.grey['400']};
  }
`;

export const UserAvatar = styled(Avatar)`
  width: 76px;
  height: 76px;
  margin-left: ${(p) => p.theme.spacing(1)};
  margin-right: ${(p) => p.theme.spacing(3)};
`;

export const UserHeader = styled(Box)`
  div {
    margin-bottom: ${(p) => p.theme.spacing(1)};
  }

  .user-name {
    white-space: nowrap;
    text-overflow: ellipsis;
    width: 233px;
    overflow: hidden;
  }
`;

export const NotificationsMenuFooter = styled(Box)`
  display: flex;
  background-color: ${(p) => p.theme.palette.grey[200]};
  padding: ${(p) => p.theme.spacing(1, 2)};

  .MuiButton-root {
    &:first-of-type {
      padding-right: ${(p) => p.theme.spacing(1)};
      margin-right: ${(p) => p.theme.spacing(1)};
      border-right: 1px solid ${(p) => p.theme.palette.grey[300]};
      border-radius: 0;
    }

    &:last-of-type {
      margin-left: auto;
    }
  }
`;
