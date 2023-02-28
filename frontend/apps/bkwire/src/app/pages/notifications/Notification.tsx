import React, { useCallback } from 'react';
import { Box, Typography } from '@mui/material';
import CircleIcon from '@mui/icons-material/Circle';
import CircleOutlinedIcon from '@mui/icons-material/CircleOutlined';
import TrendingDownOutlined from '@mui/icons-material/TrendingDownOutlined';
import ErrorOutlineOutlined from '@mui/icons-material/ErrorOutlineOutlined';
import ArticleOutlined from '@mui/icons-material/ArticleOutlined';
import { NotificationRecord } from '../../api/api.types';
import { formatDateRelative } from '../../utils/date';
import { NotificationRoot } from './Notifications.styled';
import { useReadNotification } from '../../api/api.hooks';
import { useNavigate } from 'react-router-dom';

export const Notification: React.FC<{ data: NotificationRecord }> = ({
  data,
}) => {
  const { mutate: readNotification } = useReadNotification();
  const navigate = useNavigate();

  const read = useCallback(() => {
    if (data.status === 'unread') {
      readNotification(data.id);
    }
  }, [data.status, data.id, readNotification]);

  const open = useCallback(() => {
    if (data.type === 'bk' || data.type === 'activity') {
      navigate(`/view/bankruptcy/${data.bk_id}`);
    }
  }, [data.type, data.bk_id, navigate]);

  return (
    <NotificationRoot>
      <Box className="notif-content">
        <Box className="notif-status" onClick={read}>
          {data.status === 'read' ? <CircleOutlinedIcon /> : <CircleIcon />}
        </Box>
        <Box className="notif-icon" onClick={open}>
          {data.type === 'bk' ? (
            <TrendingDownOutlined />
          ) : data.type === 'activity' ? (
            <ArticleOutlined />
          ) : (
            <ErrorOutlineOutlined />
          )}
        </Box>
        <Box className="notif-body" onClick={open}>
          <Typography className="notif-title" variant="body2" fontWeight="bold">
            {data.title}
          </Typography>
          <Typography className="notif-details" variant="body2">
            {data.body}
          </Typography>
        </Box>
        <Box className="notif-actions">
          <Typography variant="caption">
            {formatDateRelative(data.date)}
          </Typography>
        </Box>
      </Box>
    </NotificationRoot>
  );
};
