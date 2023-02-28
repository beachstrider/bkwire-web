import React, { useCallback, useEffect, useState } from 'react';
import { Box, ListItemButton, Typography } from '@mui/material';
import { PagePaper } from '../../components/PagePaper.styled';
import { Notification } from '../../pages/notifications/Notification';
import { Loading } from '../../components/loading/Loading';
import { ButtonLink } from '../../components/ButtonLink';
import {
  NotificationRecord,
  NotificationType,
  NotificationStatus,
} from '../../api/api.types';
import { Dictionary } from 'lodash';
import NotificationsIcon from '@mui/icons-material/Notifications';
import NotificationImportantOutlinedIcon from '@mui/icons-material/NotificationImportantOutlined';
import NotificationsOutlinedIcon from '@mui/icons-material/NotificationsOutlined';
import TrendingDownOutlined from '@mui/icons-material/TrendingDownOutlined';
import ErrorOutlineOutlined from '@mui/icons-material/ErrorOutlineOutlined';
import ArticleOutlined from '@mui/icons-material/ArticleOutlined';
import CheckOutlinedIcon from '@mui/icons-material/CheckOutlined';
import ClearOutlinedIcon from '@mui/icons-material/ClearOutlined';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import { NotificationFilters } from './Notifications.styled';
import {
  useReadNotifications,
  useClearNotifications,
  useGetNotifications,
} from '../../api/api.hooks';
import { format } from 'date-fns';
import _groupBy from 'lodash/groupBy';
import { Elem, useLayoutUtils } from '../../hooks/useLayoutUtils';

export const Notifications: React.FC = () => {
  const { fillHeightCss } = useLayoutUtils();

  const [filters, setFilters] = useState<{
    type: NotificationType | 'all';
    status: NotificationStatus | 'all';
  }>({ type: 'all', status: 'all' });

  const { mutate: clearNotifications } = useClearNotifications();
  const { mutate: readNotifications } = useReadNotifications();

  const { data, isLoading } = useGetNotifications(filters);
  const [notifications, setNotifications] = useState<Dictionary<
    NotificationRecord[]
  > | null>(null);

  useEffect(() => {
    setNotifications(
      _groupBy(data || [], (n) => format(new Date(n.date), 'LLLL yyyy'))
    );
  }, [data]);

  const clearAll = useCallback(() => {
    clearNotifications(filters);
  }, [clearNotifications, filters]);

  const readAll = useCallback(() => {
    readNotifications(filters);
  }, [readNotifications, filters]);

  return (
    <Box flexGrow={1}>
      <Box display="flex">
        <Typography variant="h1" my={3} display="inline-flex">
          Notifications center
        </Typography>

        <Box
          display="flex"
          gap={4}
          flexGrow={1}
          justifyContent="end"
          alignItems="start"
          pt={4}
        >
          <ButtonLink endIcon={<CheckOutlinedIcon />} onClick={readAll}>
            Mark all as read
          </ButtonLink>
          <ButtonLink endIcon={<ClearOutlinedIcon />} onClick={clearAll}>
            Clear all
          </ButtonLink>
          <ButtonLink endIcon={<SettingsOutlinedIcon />} to="/account/alerts">
            Manage settings
          </ButtonLink>
        </Box>
      </Box>

      <Box display="flex">
        <PagePaper width={240} mb={2} mr={2}>
          <Box display="flex" justifyContent="space-between" height={48} px={2}>
            <Typography variant="body2" fontWeight="bold" alignSelf="center">
              Notifications
            </Typography>
            <ButtonLink onClick={clearAll}>Clear all</ButtonLink>
          </Box>
          <NotificationFilters>
            <ListItemButton
              selected={filters.status === 'all' && filters.type === 'all'}
              onClick={() => setFilters({ status: 'all', type: 'all' })}
            >
              <NotificationsIcon />
              <Typography variant="body2">All notifications</Typography>
            </ListItemButton>
            <ListItemButton
              selected={filters.status === 'unread'}
              onClick={() => setFilters({ status: 'unread', type: 'all' })}
            >
              <NotificationImportantOutlinedIcon />
              <Typography variant="body2">Unread</Typography>
            </ListItemButton>
            <ListItemButton
              selected={filters.status === 'read'}
              onClick={() => setFilters({ status: 'read', type: 'all' })}
            >
              <NotificationsOutlinedIcon />
              <Typography variant="body2">Read</Typography>
            </ListItemButton>
            <ListItemButton
              selected={filters.type === 'bk'}
              onClick={() => setFilters({ status: 'all', type: 'bk' })}
            >
              <TrendingDownOutlined />
              <Typography variant="body2">New bankruptcies</Typography>
            </ListItemButton>
            <ListItemButton
              selected={filters.type === 'activity'}
              onClick={() => setFilters({ status: 'all', type: 'activity' })}
            >
              <ArticleOutlined />
              <Typography variant="body2">Activity alerts</Typography>
            </ListItemButton>
            <ListItemButton
              selected={filters.type === 'system'}
              onClick={() => setFilters({ status: 'all', type: 'system' })}
            >
              <ErrorOutlineOutlined />
              <Typography variant="body2">App status</Typography>
            </ListItemButton>
          </NotificationFilters>
        </PagePaper>

        <PagePaper
          flexGrow={1}
          minHeight={fillHeightCss(Elem.Header | Elem.Heading)}
          mb={2}
        >
          {isLoading ? (
            <Loading />
          ) : !data?.length ? (
            <Box
              width="100%"
              height="100%"
              display="flex"
              justifyContent="center"
              alignItems="center"
            >
              <Box display="flex" flexDirection="column" alignItems="center">
                <Typography variant="h1">Nothing here yet</Typography>
                <Typography variant="h3">
                  New notifications will be shown here as soon as they come in
                </Typography>
              </Box>
            </Box>
          ) : (
            notifications &&
            Object.entries(notifications).map(([k, g]) => (
              <Box key={k}>
                <Box p={2}>
                  <Typography variant="body2" fontWeight="bold">
                    {k === 'bk'
                      ? 'Bankruptcy'
                      : k === 'activity'
                      ? 'Activity'
                      : 'System'}
                  </Typography>
                </Box>
                {g.map((n) => (
                  <Notification key={n.id} data={n} />
                ))}
              </Box>
            ))
          )}
        </PagePaper>
      </Box>
    </Box>
  );
};
