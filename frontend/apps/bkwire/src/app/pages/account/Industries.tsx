import React, { useCallback, useEffect, useState } from 'react';
import { Typography, Box, useTheme } from '@mui/material';
import { SelectMatrix } from '../../components/selectMatrix/SelectMatrix';
import { ButtonLink } from '../../components/ButtonLink';
import { Factory } from '@mui/icons-material';
import {
  useGetIndustries,
  useGetViewer,
  useUpdateUserIndustries,
} from '../../api/api.hooks';
import { useSnackbar } from 'notistack';
import { Loading } from '../../components/loading/Loading';

export const Industries: React.VFC = () => {
  const theme = useTheme();
  const [userIndustries, setUserIndustries] = useState<number[]>([]);
  const { data, isLoading: industriesLoading } = useGetIndustries();
  const { enqueueSnackbar } = useSnackbar();
  const { data: viewer } = useGetViewer();
  const { mutate: updateUserIndustries, status } = useUpdateUserIndustries();

  useEffect(() => {
    if (status === 'success') {
      enqueueSnackbar('Your BKwire Zones were updated successfully!', {
        variant: 'success',
      });
    } else if (status === 'error') {
      enqueueSnackbar('There was a problem updating your BKwire Zones!', {
        variant: 'error',
      });
    }
  }, [enqueueSnackbar, status]);

  useEffect(() => {
    setUserIndustries(
      viewer?.industry_naics_code?.split(',').map(Number) || []
    );
  }, [viewer?.industry_naics_code]);

  const handleSubmit = useCallback(() => {
    updateUserIndustries(userIndustries);
  }, [updateUserIndustries, userIndustries]);

  return !viewer || industriesLoading ? (
    <Loading />
  ) : (
    <Box
      display="flex"
      flexDirection="column"
      flexGrow={1}
      position="relative"
      px={12}
      py={4}
    >
      <Box
        width="100%"
        height={200}
        bgcolor={(t) => t.palette.grey[100]}
        position="absolute"
        top={0}
        left={0}
        zIndex={0}
      />
      <Box display="flex" alignItems="end" mb={10} zIndex={1}>
        <Factory
          sx={{
            fontSize: 130,
            ml: '-10px',
            mr: 4,
            color: theme.palette.grey[300],
          }}
        />
        <Typography variant="h1" m={0}>
          Choose BKwire Zones to watch
        </Typography>
      </Box>

      <Box width="100%" flexGrow={1} flexShrink={0}>
        <Box mb={3}>
          <SelectMatrix
            columns={6}
            options={data || []}
            selected={userIndustries}
            setSelected={setUserIndustries}
          />
        </Box>

        <Box display="flex" justifyContent="end">
          <ButtonLink
            to=""
            variant="contained"
            minWidth={216}
            minHeight={48}
            isLoading={status === 'loading'}
            disabled={!userIndustries.length}
            onClick={handleSubmit}
          >
            Update
          </ButtonLink>
        </Box>
      </Box>
    </Box>
  );
};
