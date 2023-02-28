import React, { useState, useRef, useCallback } from 'react';
import { Box, Typography, useTheme } from '@mui/material';
import { ButtonLink } from '../../components/ButtonLink';
import { AddAlert } from '@mui/icons-material';
import { useGetViewer } from '../../api/api.hooks';
import { Loading } from '../../components/loading/Loading';
import { useSnackbar } from 'notistack';
import { AlertsForm, AlertsFormHandle } from './AlertsForm';

export const Alerts: React.VFC = () => {
  const theme = useTheme();
  const { enqueueSnackbar } = useSnackbar();

  const { data: viewer, isLoading: isViewerLoading } = useGetViewer();

  const [isFormValid, setIsFormValid] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const formHandle = useRef<AlertsFormHandle | null>(null);

  const onLoading = useCallback(() => {
    setIsLoading(true);
  }, [setIsLoading]);

  const onSuccess = useCallback(() => {
    setIsLoading(false);
    enqueueSnackbar('Alerts were updated successfully!', {
      variant: 'success',
    });
  }, [enqueueSnackbar, setIsLoading]);

  const onError = useCallback(() => {
    setIsLoading(false);
    enqueueSnackbar('There was a problem updating your alerts!', {
      variant: 'error',
    });
  }, [enqueueSnackbar, setIsLoading]);

  return (
    <Box
      display="flex"
      flexDirection="column"
      flexGrow={1}
      py={4}
      px={8}
      position="relative"
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

      <Box display="flex" alignItems="end" mb={6} ml={4} zIndex={1}>
        <AddAlert
          sx={{
            fontSize: 130,
            ml: '-10px',
            mr: 4,
            color: theme.palette.grey[300],
          }}
        />
        <Typography variant="h1" m={0}>
          Choose how you want to be notified
        </Typography>
      </Box>

      {isViewerLoading || !viewer ? (
        <Box display="flex" p={4}>
          <Loading />
        </Box>
      ) : (
        <Box display="grid" gridTemplateColumns="1fr 1fr" gap={2}>
          <AlertsForm
            ref={formHandle}
            viewer={viewer}
            setIsFormValid={setIsFormValid}
            onLoading={onLoading}
            onSuccess={onSuccess}
            onError={onError}
          />
        </Box>
      )}

      <Box display="flex" justifyContent="end" pr={4} pt={4}>
        <ButtonLink
          to=""
          variant="contained"
          minWidth={216}
          minHeight={48}
          isLoading={isLoading}
          disabled={!isFormValid || isLoading}
          onClick={() => formHandle.current?.submitForm()}
          sx={{ transform: 'translateY(-24px)' }}
        >
          Update
        </ButtonLink>
      </Box>
    </Box>
  );
};
