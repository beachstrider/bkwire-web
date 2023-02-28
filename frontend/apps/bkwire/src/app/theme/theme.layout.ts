import { Theme } from '@mui/system';

const getLayout = (theme: Theme) => ({
  breakpoints: {
    values: { xs: 0, sm: 600, md: 960, lg: 1340, xl: 1920 },
  },
  spacing: 8,
  shape: { borderRadius: 4 },
});

export default getLayout;
