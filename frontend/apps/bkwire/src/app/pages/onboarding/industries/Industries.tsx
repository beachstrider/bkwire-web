import React, { useState, useEffect } from 'react';
import { Box, Typography } from '@mui/material';
import _includes from 'lodash/includes';
import { ButtonLink } from '../../../components/ButtonLink';
import { SelectMatrix } from '../../../components/selectMatrix/SelectMatrix';
import { PagePaper } from '../../../components/PagePaper.styled';
import {
  useGetIndustries,
  useGetViewer,
  useUpdateUserIndustries,
} from '../../../api/api.hooks';
import { useNavigate } from 'react-router';
import { useSnackbar } from 'notistack';
import { Loading } from '../../../components/loading/Loading';
import bkwirelogo from '../../../../assets/bkwirelogo2.png';

export const Industries: React.VFC = () => {
  const navigate = useNavigate();
  const [userIndustries, setUserIndustries] = useState<number[]>([]);
  const { data, isLoading: industriesLoading } = useGetIndustries();
  const { enqueueSnackbar } = useSnackbar();
  const { data: viewer } = useGetViewer();
  const { mutate: updateUserIndustries, status } = useUpdateUserIndustries();

  const onUpdate = () => {
    updateUserIndustries(userIndustries);
  };

  useEffect(() => {
    if (status === 'success') {
      navigate('/onboarding/alerts');
    } else if (status === 'error') {
      enqueueSnackbar('There was a problem updating your BKwire Zones!', {
        variant: 'error',
      });
    }
  }, [enqueueSnackbar, navigate, status]);

  useEffect(() => {
    if (viewer) {
      setUserIndustries(
        viewer?.industry_naics_code?.split(',').map(Number) || []
      );
    }
  }, [navigate, viewer]);

  return (
    <>
      <Box display="flex" gap={2} alignItems="end" mb={4}>
        <Typography
          component="h1"
          variant="greeting"
          sx={{ fontWeight: 'bold', marginBottom: '-6px' }}
        >
          Welcome to
        </Typography>

        <img src={bkwirelogo} alt="BKwire logo" width={380} />
      </Box>

      <Typography
        component="h1"
        variant="greeting"
        textAlign="center"
        sx={{ fontSize: 28 }}
      >
        Select the BKwire Zones that interest you.
      </Typography>

      <Typography variant="subtitle" textAlign="center" mb={2}>
        You can update your BKwire Zones anytime via profile settings.
      </Typography>

      {!viewer || industriesLoading ? (
        <PagePaper display="flex" p={4} width="100%">
          <Loading />
        </PagePaper>
      ) : (
        <>
          <PagePaper width="100%">
            <SelectMatrix
              options={data || []}
              selected={userIndustries}
              setSelected={setUserIndustries}
            />
          </PagePaper>

          <Box mt={4}>
            <ButtonLink
              variant="contained"
              minWidth={216}
              minHeight={48}
              isLoading={status === 'loading'}
              disabled={!userIndustries.length}
              onClick={onUpdate}
            >
              Continue
            </ButtonLink>
          </Box>
        </>
      )}
    </>
  );
};
