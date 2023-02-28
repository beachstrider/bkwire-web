import { Box, List, ListItem, ListItemText } from '@mui/material';
import React, { useCallback } from 'react';
import { MenuTabPanel, NotificationsMenuFooter } from './SecondaryMenu.styled';
import { Notification } from '../../pages/notifications/Notification';
import { Loading } from '../../components/loading/Loading';
import {
  useClearNotifications,
  useGetNotifications,
  useReadNotifications,
} from '../../api/api.hooks';
import { useNavigate } from 'react-router';
import { ButtonLink } from '../../components/ButtonLink';
import { NotificationStatus, NotificationType } from '../../api/api.types';

export const HEADER_NOTIFICATION_FILTERS: {
  type: NotificationType | 'all';
  status: NotificationStatus | 'all';
  limit?: number;
} = {
  type: 'all',
  status: 'all',
  limit: 6,
};

interface NotificationsMenuProps {
  close: () => void;
}
export const NotificationsMenu: React.FC<NotificationsMenuProps> = ({
  close,
}) => {
  const navigate = useNavigate();

  const { mutate: clearNotifications } = useClearNotifications();
  const { mutate: readNotifications } = useReadNotifications();

  const { data, isLoading } = useGetNotifications(HEADER_NOTIFICATION_FILTERS);

  const viewAll = () => {
    close();
    navigate('/notifications');
  };

  const clearAll = useCallback(() => {
    clearNotifications(HEADER_NOTIFICATION_FILTERS);
  }, [clearNotifications]);

  const readAll = useCallback(() => {
    readNotifications(HEADER_NOTIFICATION_FILTERS);
  }, [readNotifications]);

  return (
    <MenuTabPanel>
      <List component="div">
        <ListItem component="div">
          <ListItemText primary="Notifications" />
        </ListItem>
      </List>
      {isLoading ? (
        <Box p={4}>
          <Loading />
        </Box>
      ) : (data || []).length ? (
        <Box>
          {(data || []).map((n) => (
            <Notification key={n.id} data={n} />
          ))}
        </Box>
      ) : (
        <Box p={2}>Nothing here. You are all caught up!</Box>
      )}
      <NotificationsMenuFooter>
        <ButtonLink onClick={readAll}>Mark all read</ButtonLink>
        <ButtonLink onClick={clearAll}>Clear all</ButtonLink>
        <ButtonLink onClick={viewAll}>View all</ButtonLink>
      </NotificationsMenuFooter>
    </MenuTabPanel>
  );
};
