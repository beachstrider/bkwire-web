import React from 'react';
import { YoutubeEmbedRoot } from './YoutubeEmbed.styled';

export interface YoutubeEmbedProps {
  id: string;
  title?: string;
  width?: number;
  height?: number;
  allowFullscreen?: boolean;
}

export const YoutubeEmbed: React.FC<YoutubeEmbedProps> = ({
  id,
  title = '',
  width = 960,
  height = 540,
  allowFullscreen = false,
}) => (
  <YoutubeEmbedRoot>
    <iframe
      width={width}
      height={height}
      src={`https://www.youtube.com/embed/${id}`}
      frameBorder="0"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowFullScreen={allowFullscreen}
      title={title}
    />
  </YoutubeEmbedRoot>
);
