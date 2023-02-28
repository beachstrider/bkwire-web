import React, { useCallback, useRef, useState } from 'react';
import { Box, Typography } from '@mui/material';
import { ButtonLink } from '../../../components/ButtonLink';
import { PagePaper } from '../../../components/PagePaper.styled';
import { useSnackbar } from 'notistack';
import { useNavigate } from 'react-router';
import { ProfileForm, ProfileFormHandle } from '../../account/ProfileForm';

export const YourCompany: React.VFC = () => {
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  const [isLoading, setIsLoading] = useState(false);
  const [isValid, setIsValid] = useState(false);

  const formHandle = useRef<ProfileFormHandle | null>(null);

  const onSuccess = useCallback(() => {
    navigate('/dashboard');
  }, [navigate]);

  const onError = useCallback(() => {
    enqueueSnackbar('There was a problem updating your details!', {
      variant: 'error',
    });
  }, [enqueueSnackbar]);

  return (
    <>
      <Typography component="h1" variant="greeting" textAlign="center">
        Just one more optional item for BKwire
      </Typography>

      <Typography variant="subtitle" textAlign="center">
        Providing BKwire the below information provides the best user experience
      </Typography>

      <>
        <PagePaper my={4} p={4} pr={5} width="100%">
          <Box display="flex" gap={2} mb={1}>
            <Box
              display="flex"
              alignItems="center"
              justifyContent="end"
              width={48}
            />
            <Box flexGrow={1}>
              <Typography variant="h3" mb={1}>
                Tell BKwire about your company
              </Typography>

              <Typography variant="body2" fontWeight="bold">
                Check out our <ButtonLink to="#">privacy policy</ButtonLink>
              </Typography>
            </Box>
          </Box>

          <ProfileForm
            ref={formHandle}
            completeOnboarding
            onLoading={setIsLoading}
            onValidate={setIsValid}
            onSuccess={onSuccess}
            onError={onError}
          />
        </PagePaper>

        <Box display="flex" gap={2}>
          <ButtonLink
            to="/onboarding/alerts"
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
            disabled={!isValid || isLoading}
            isLoading={isLoading}
            onClick={() => formHandle.current?.submitForm()}
          >
            Continue
          </ButtonLink>
        </Box>
      </>
    </>
  );
};
