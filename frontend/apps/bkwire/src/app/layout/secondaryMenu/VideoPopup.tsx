import React from 'react';
import { Box, IconButton, Typography } from '@mui/material';
import { VideoPopupRoot } from './HelpMenu.styled';
import { Close } from '@mui/icons-material';
import { YoutubeEmbed } from '../../components/youtubeEmbed/YoutubeEmbed';

export const videos: Record<string, { id: string; title: string }> = {
  tour: {
    id: 'XOZN7A5IYYw',
    title: 'Product Tour',
  },
  zones: {
    id: 'UB7AUTxUMp8',
    title: 'BKwire Zones',
  },
  watchlist:{
    id: 'IuO9URmc630',
    title: 'BKwire Watchlist',
  },
  
} as const;

export type VideoType = keyof typeof videos;

export const VideoPopup = ({
  type,
  open,
  onClose,
}: {
  type: VideoType;
  open: boolean;
  onClose: () => void;
}) => (
  <VideoPopupRoot open={open} onClose={onClose}>
    <IconButton className="modal-close" onClick={onClose}>
      <Close />
    </IconButton>
    <Box display="flex" flexDirection="column">
      <Box className="modal-header">
        <Typography variant="h2" py={2} fontSize="1.75rem">
          {videos[type].title}
        </Typography>
      </Box>
      <Box className="modal-body">
        <YoutubeEmbed
          id={videos[type].id}
          title={videos[type].title}
          allowFullscreen
        />
      </Box>
    </Box>
  </VideoPopupRoot>
);
