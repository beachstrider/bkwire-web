import React, { useEffect } from 'react';
import { PasswordTwoTone } from '@mui/icons-material';
import { Box, TextField, Typography } from '@mui/material';
import * as yup from 'yup';
import { FormControl } from '../onboarding/Onboarding.styled';
import { useForm } from '../../hooks/useForm';
import { useAuth0 } from '@auth0/auth0-react';
import { ButtonLink } from '../../components/ButtonLink';
import { useSnackbar } from 'notistack';
import { useGetViewer, useChangePassword } from '../../api/api.hooks';
import { Loading } from '../../components/loading/Loading';
import { SpecialHint } from './Account.styled';

const validationSchema = yup.object({
  newPassword: yup.string().required('This field is required!'),
});

export const PasswordForm: React.VFC = () => {
  const { user } = useAuth0();
  const { enqueueSnackbar } = useSnackbar();
  const { data: viewer } = useGetViewer();
  const { mutate: updatePassword, status } = useChangePassword();

  // define form
  const { values, touched, errors, isValid, handleChange, handleSubmit } =
    useForm({
      initialValues: {
        newPassword: '',
      },
      validationSchema: validationSchema,
      onSubmit: (values) => {
        updatePassword(values.newPassword);
      },
    });

  // handle events
  useEffect(() => {
    if (status === 'success') {
      enqueueSnackbar('Your password was changed successfully!', {
        variant: 'success',
      });
    } else if (status === 'error') {
      enqueueSnackbar('There was a problem changing your password!', {
        variant: 'error',
      });
    }
  }, [enqueueSnackbar, status]);

  return !viewer || !user ? (
    <Loading />
  ) : (
    <>
      {Boolean(viewer.is_social) && (
        <SpecialHint mt={1} mb={2} ml={8}>
          <Typography component="h3" variant="body2" fontWeight="bold" mb={1}>
            Tip!
          </Typography>
          <Typography variant="body2">
            This feature is only available for{' '}
            <strong>username / password</strong> accounts.
            <br />
            You signed in via a social provider.
          </Typography>
        </SpecialHint>
      )}

      <Box display="flex" gap={2} mb={2}>
        <Box
          display="flex"
          flexShrink={0}
          justifyContent="end"
          width={48}
          mt={2}
        >
          <PasswordTwoTone />
        </Box>
        <Box flexGrow={1}>
          <FormControl>
            <TextField
              type="password"
              size="small"
              name="newPassword"
              label="New Password"
              error={touched.newPassword && Boolean(errors.newPassword)}
              value={values.newPassword}
              onChange={handleChange}
              disabled={Boolean(viewer.is_social)}
              helperText={touched.newPassword && errors.newPassword}
            />
          </FormControl>
        </Box>
      </Box>

      <Box display="flex" justifyContent="end">
        <ButtonLink
          to=""
          variant="contained"
          minWidth={216}
          minHeight={48}
          isLoading={status === 'loading'}
          disabled={!isValid || Boolean(viewer.is_social)}
          onClick={handleSubmit}
        >
          Change password
        </ButtonLink>
      </Box>
    </>
  );
};
