import React, { useCallback, useRef, useState } from 'react';
import { LockReset } from '@mui/icons-material';
import { Avatar, Box, Typography, useTheme } from '@mui/material';
import { getInitials } from '../../utils/string';
import { useAuth0 } from '@auth0/auth0-react';
import { ButtonLink } from '../../components/ButtonLink';
import { useSnackbar } from 'notistack';
import { useGetViewer } from '../../api/api.hooks';
import { Loading } from '../../components/loading/Loading';
import { ProfileForm, ProfileFormHandle } from './ProfileForm';
import { PasswordForm } from './PasswordForm';

export const Profile: React.VFC = () => {
  const { user } = useAuth0();
  const theme = useTheme();
  const { enqueueSnackbar } = useSnackbar();
  const { data: viewer } = useGetViewer();

  const [isLoading, setIsLoading] = useState(false);
  const [isValid, setIsValid] = useState(false);

  const formHandle = useRef<ProfileFormHandle | null>(null);

  const onSuccess = useCallback(() => {
    enqueueSnackbar('Your details were updated successfully!', {
      variant: 'success',
    });
  }, [enqueueSnackbar]);

  const onError = useCallback(() => {
    enqueueSnackbar('There was a problem updating your details!', {
      variant: 'error',
    });
  }, [enqueueSnackbar]);

  return !viewer || !user ? (
    <Loading />
  ) : (
    <Box
      display="flex"
      justifyContent="center"
      flexGrow={1}
      position="relative"
      py={3}
      pl={8}
      pr={12}
      gap={4}
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
      <Box display="flex" flexDirection="column" width="50%" zIndex={1}>
        <Box display="flex" mt={3} mb={10} ml={3} gap={4} alignItems="end">
          <Avatar
            sx={{
              width: 112,
              height: 112,
              backgroundImage: `url("${user.picture}")`,
              backgroundSize: 'cover',
              transform: 'translateY(-4px)',
            }}
          >
            {!user.picture && (
              <Typography variant="greeting">
                {getInitials(`${viewer.first_name} ${viewer.last_name}`)}
              </Typography>
            )}
          </Avatar>

          <Typography variant="h1" mb={0}>
            Change profile data
          </Typography>
        </Box>

        <ProfileForm
          ref={formHandle}
          validateOnLoad
          onLoading={setIsLoading}
          onValidate={setIsValid}
          onSuccess={onSuccess}
          onError={onError}
        />

        <Box display="flex" justifyContent="end">
          <ButtonLink
            to=""
            variant="contained"
            minWidth={216}
            minHeight={48}
            isLoading={isLoading}
            disabled={!isValid || isLoading}
            onClick={() => formHandle.current?.submitForm()}
          >
            Update
          </ButtonLink>
        </Box>
      </Box>

      <Box display="flex" flexDirection="column" width="50%" zIndex={1}>
        <Box display="flex" alignItems="end" mb={8} ml={3} gap={2}>
          <LockReset
            sx={{
              fontSize: 150,
              ml: '-10px',
              mt: '2px',
              color: theme.palette.grey[300],
            }}
          />
          <Typography variant="h1" mb={2}>
            Change your password
          </Typography>
        </Box>

        <PasswordForm />
      </Box>
    </Box>
  );
};
