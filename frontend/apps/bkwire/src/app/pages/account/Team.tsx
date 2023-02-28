import React, { useEffect } from 'react';
import {
  Groups,
  EmailTwoTone,
  PersonTwoTone,
  PersonOffTwoTone,
} from '@mui/icons-material';
import { Box, TextField, Typography, useTheme } from '@mui/material';
import * as yup from 'yup';
import { FormControl } from '../onboarding/Onboarding.styled';
import { useForm } from '../../hooks/useForm';
import { ButtonLink } from '../../components/ButtonLink';
import { useSnackbar } from 'notistack';
import {
  useAddTeamMember,
  useGetViewer,
  useRemoveTeamMember,
} from '../../api/api.hooks';
import { Loading } from '../../components/loading/Loading';
import { SpecialHint } from './Account.styled';

const validationSchema = yup.object({
  email: yup
    .string()
    .email('Please enter a valid email!')
    .required('This field is required!'),
});

interface FormData {
  email: string;
}

export const Team: React.VFC = () => {
  const theme = useTheme();
  const { enqueueSnackbar } = useSnackbar();
  const { data: viewer, isLoading: viewerLoading } = useGetViewer();
  const {
    mutate: addTeamMember,
    status: addTeamMemberStatus,
    isLoading: addTeamMemberLoading,
    error: addTeamMemberError,
    data: addTeamMemberRes,
  } = useAddTeamMember();
  const {
    mutate: removeTeamMember,
    status: removeTeamMemberStatus,
    isLoading: removeTeamMemberLoading,
    error: removeTeamMemberError,
    data: removeTeamMemberRes,
  } = useRemoveTeamMember();

  const {
    values,
    setFieldValue,
    touched,
    errors,
    isValid,
    handleChange,
    handleSubmit: addMember,
  } = useForm<FormData>({
    initialValues: {
      email: '',
    },
    validationSchema,
    onSubmit: (values) => {
      addTeamMember(values.email);
    },
  });

  useEffect(() => {
    if (addTeamMemberStatus === 'success') {
      setFieldValue('email', '', false);
      const message =
        addTeamMemberRes?.data?.toString() || 'Team member added successfully!';
      enqueueSnackbar(message, {
        variant: message.indexOf('success') !== -1 ? 'success' : 'error',
      });
    } else if (addTeamMemberStatus === 'error') {
      enqueueSnackbar(
        (addTeamMemberError as { message: string })?.message ||
          'There was a problem adding the team member!',
        {
          variant: 'error',
        }
      );
    }
  }, [
    enqueueSnackbar,
    addTeamMemberStatus,
    addTeamMemberError,
    setFieldValue,
    addTeamMemberRes,
  ]);

  useEffect(() => {
    if (removeTeamMemberStatus === 'success') {
      const message =
        removeTeamMemberRes?.data?.toString() ||
        'Team member removed successfully!';
      enqueueSnackbar(message, {
        variant: message.indexOf('success') !== -1 ? 'success' : 'error',
      });
    } else if (removeTeamMemberStatus === 'error') {
      enqueueSnackbar(
        (removeTeamMemberError as { message: string })?.message ||
          'There was a problem removing the team member!',
        {
          variant: 'error',
        }
      );
    }
  }, [
    enqueueSnackbar,
    removeTeamMemberStatus,
    removeTeamMemberError,
    removeTeamMemberRes,
  ]);

  const isAddingMember = viewerLoading || !viewer || addTeamMemberLoading;
  const isRemovingMember = viewerLoading || !viewer || removeTeamMemberLoading;

  const team = (viewer?.team || '').split(',').filter((e) => Boolean(e));

  const disabled = viewer?.max_team_count === 0;

  return viewerLoading || !viewer ? (
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
        <Box display="flex" alignItems="end" mb={10} mt={3} zIndex={1}>
          <Groups
            sx={{
              fontSize: 114,
              ml: 2.5,
              mr: 4,
              color: theme.palette.grey[300],
              border: '2px solid',
              borderColor: theme.palette.grey[300],
              borderRadius: '50%',
            }}
          />
          <Box>
            <Typography variant="h1" m={0}>
              Manage your team
            </Typography>
            <Typography variant="body1">
              This feature is only available for the <strong>TEAM</strong> and{' '}
              <strong>MVP</strong> subscriptions.
            </Typography>
          </Box>
        </Box>

        {!team.length && (
          <Box display="flex" gap={2} mb={2} alignItems="center">
            <Box display="flex" flexShrink={0} justifyContent="end" width={48}>
              <PersonOffTwoTone />
            </Box>
            <Box flexGrow={1}>
              <Typography variant="body1">
                <b>Nobody here yet.</b> Register some emails using the form
                below.
              </Typography>
            </Box>
          </Box>
        )}

        {team.map((e) => (
          <Box key={e} display="flex" gap={2} mb={2} alignItems="center">
            <Box display="flex" flexShrink={0} justifyContent="end" width={48}>
              <PersonTwoTone />
            </Box>
            <Box flexGrow={1}>
              <Typography variant="body1">{e}</Typography>
            </Box>

            <ButtonLink
              variant="contained"
              disabled={isAddingMember || isRemovingMember}
              isLoading={isRemovingMember}
              onClick={() => removeTeamMember(e)}
            >
              Remove
            </ButtonLink>
          </Box>
        ))}

        <Box display="flex" gap={2} mb={2} mt={1}>
          <Box
            display="flex"
            flexShrink={0}
            justifyContent="end"
            width={48}
            mt={2}
          >
            <EmailTwoTone />
          </Box>
          <Box flexGrow={1}>
            <FormControl>
              <TextField
                size="small"
                name="email"
                label="New member email"
                disabled={disabled || Boolean(viewer.subscription_inherited)}
                error={touched.email && Boolean(errors.email)}
                value={values.email}
                onChange={handleChange}
                helperText={touched.email && errors.email}
              />
            </FormControl>
          </Box>
        </Box>
        <Box display="flex" justifyContent="end">
          <ButtonLink
            variant="contained"
            minWidth={216}
            minHeight={48}
            disabled={
              !isValid ||
              isAddingMember ||
              isRemovingMember ||
              disabled ||
              Boolean(viewer.subscription_inherited)
            }
            isLoading={isAddingMember}
            onClick={addMember}
          >
            Add team member
          </ButtonLink>
        </Box>
      </Box>

      <Box display="flex" flexDirection="column" width="50%" zIndex={1}>
        <Box display="flex" flexDirection="column" mb={8} ml={3} gap={2}>
          {viewer.subscription_inherited ? (
            <>
              <SpecialHint mt={27.1}>
                <Typography
                  component="h3"
                  variant="body2"
                  fontWeight="bold"
                  mb={1}
                >
                  Your subscription is inherited
                </Typography>
                <Typography variant="body2">
                  You are accessing <strong>BKwire</strong> as part of a team.
                </Typography>
              </SpecialHint>

              <Typography variant="body1">
                This means you cannot manage the subscription or your own team.
              </Typography>
              <Typography variant="body1">
                In order to have your own subscription and team, you first need
                to be removed from your current team.
              </Typography>
              <Typography variant="body1">
                This feature is only available for the <strong>TEAM</strong> and{' '}
                <strong>ENTERPRISE</strong> subscriptions.
              </Typography>
            </>
          ) : (
            <SpecialHint mt={27.1}>
              <Typography
                component="h3"
                variant="body2"
                fontWeight="bold"
                mb={1}
              >
                Did you know?
              </Typography>
              <Typography variant="body2">
                The emails registered in here can login into{' '}
                <strong>BKwire</strong> and will have access to all the features
                enabled by your current subscription. You are virtually sharing
                your subscription with your team.
              </Typography>
            </SpecialHint>
          )}
        </Box>
      </Box>
    </Box>
  );
};
