import React, { useCallback, useRef, useState } from 'react';
import { Box, Typography } from '@mui/material';
import { ButtonLink } from '../../../components/ButtonLink';
import { PagePaper } from '../../../components/PagePaper.styled';
import { AlertsForm, AlertsFormHandle } from '../../account/AlertsForm';
import { useNavigate } from 'react-router';
import { useSnackbar } from 'notistack';
import { Loading } from '../../../components/loading/Loading';
import { useGetViewer } from '../../../api/api.hooks';

export const Alerts: React.VFC = () => {
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  const { data: viewer, isLoading: isViewerLoading } = useGetViewer();

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isFormValid, setIsFormValid] = useState<boolean>(false);

  const formHandle = useRef<AlertsFormHandle>(null);

  const onLoading = useCallback(() => {
    setIsLoading(true);
  }, [setIsLoading]);

  const onSuccess = useCallback(() => {
    setIsLoading(false);
    navigate('/onboarding/yourcompany');
  }, [navigate, setIsLoading]);

  const onError = useCallback(() => {
    setIsLoading(false);
    enqueueSnackbar('There was a problem updating your alerts!', {
      variant: 'error',
    });
  }, [enqueueSnackbar]);

  return (
    <>
      <Typography component="h1" variant="greeting" textAlign="center">
        BKwire Notifications
      </Typography>

      <Typography variant="subtitle" textAlign="center">
        You can update preferences anytime via profile settings.
      </Typography>

      <Typography
        variant="h3"
        fontWeight="bold"
        alignSelf="start"
        mt={3}
        mb={2}
      >
        BKwire notification preferences
      </Typography>

      <PagePaper
        mb={4}
        pr={5}
        width="100%"
        display="flex"
        flexDirection="column"
      >
        {isViewerLoading || !viewer ? (
          <Box display="flex" p={4}>
            <Loading />
          </Box>
        ) : (
          <AlertsForm
            ref={formHandle}
            viewer={viewer}
            setIsFormValid={setIsFormValid}
            onLoading={onLoading}
            onSuccess={onSuccess}
            onError={onError}
            reorder
          />
        )}
      </PagePaper>

      <Box display="flex" gap={2}>
        <ButtonLink
          to="/onboarding/industries"
          variant="outlined"
          minWidth={144}
          minHeight={48}
        >
          Back
        </ButtonLink>
        <ButtonLink
          variant="contained"
          minWidth={216}
          minHeight={48}
          isLoading={isLoading}
          disabled={!isFormValid || isLoading}
          onClick={() => formHandle.current?.submitForm()}
        >
          Continue
        </ButtonLink>
      </Box>
    </>
  );
};
