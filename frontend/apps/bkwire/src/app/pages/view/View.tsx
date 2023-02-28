import { Box, Theme, Typography, useTheme } from '@mui/material';
import { BoxProps } from '@mui/system';
import { Routes, Route } from 'react-router-dom';
import { Bankruptcy } from '../view/Bankruptcy';
import { Company } from '../view/Company';
import { InfoBoxContentRoot, InfoBoxRoot } from './View.styled';

export interface InfoBoxContentProps {
  value: string;
  label?: string;
  caption?: string;
  color?: (theme: Theme) => string;
  labelAdornment?: React.ReactNode;
  width?: string;
  onClick?: () => void;
}

export interface InfoBoxProps {
  title: string;
  icon?: React.ReactNode;
}

export const InfoBoxContent: React.FC<InfoBoxContentProps> = ({
  value,
  label = '',
  caption = '',
  color,
  labelAdornment,
  width,
  onClick,
}) => {
  const theme = useTheme();
  return (
    <InfoBoxContentRoot width={width}>
      <Box className="info-box-label">
        <Typography variant="body2">{label}</Typography>
        <Box className="info-box-label-adornment">{labelAdornment}</Box>
      </Box>
      <Typography
        variant="h1"
        color={color?.(theme)}
        fontSize={value.length > 15 ? 20 : undefined}
        onClick={() => onClick?.()}
        sx={{ cursor: onClick ? 'pointer' : 'auto' }}
      >
        {value}
      </Typography>
      <Typography variant="caption">{caption}</Typography>
    </InfoBoxContentRoot>
  );
};

export const InfoBox: React.FC<InfoBoxProps & BoxProps> = ({
  title,
  icon,
  children,
  ...boxProps
}) => (
  <InfoBoxRoot {...boxProps}>
    <Box className="info-box-header">
      <Typography variant="h2">{title}</Typography>
      {icon}
    </Box>
    {children}
  </InfoBoxRoot>
);

export const View = () => (
  <Routes>
    <Route path="/bankruptcy/:id" element={<Bankruptcy />} />
    <Route path="/company" element={<Company />} />
  </Routes>
);
