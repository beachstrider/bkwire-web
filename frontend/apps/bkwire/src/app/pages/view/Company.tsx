import { Box, Typography } from '@mui/material';
import { PagePaper } from '../../components/PagePaper.styled';

export const Company = () => {
  return (
    <Box display="flex" flexDirection="column" flexGrow={1}>
      <Typography variant="h1" my={3}>
        Acme Foods Company
      </Typography>

      <PagePaper p={2} height={'calc(100% - 106px)'}>
        <Typography variant="h2">Company details</Typography>
      </PagePaper>
    </Box>
  );
};
