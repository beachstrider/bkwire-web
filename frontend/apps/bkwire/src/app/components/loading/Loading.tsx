import CircularProgress from '@mui/material/CircularProgress';
import { LoadingRoot } from './Loading.styled';

interface LoadingProps {
  size?: number | string;
  color?:
    | 'primary'
    | 'secondary'
    | 'error'
    | 'info'
    | 'success'
    | 'warning'
    | 'inherit';
}
export const Loading: React.FC<LoadingProps> = ({ size, color }) => (
  <LoadingRoot className="loading-spinner">
    <CircularProgress size={size} color={color} />
  </LoadingRoot>
);
