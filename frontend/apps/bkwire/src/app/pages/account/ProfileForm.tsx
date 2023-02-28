import React, { useEffect, useImperativeHandle } from 'react';
import {
  AddLocationTwoTone,
  BadgeTwoTone,
  BusinessTwoTone,
  EmailTwoTone,
  PhoneTwoTone,
  MiscellaneousServicesTwoTone,
} from '@mui/icons-material';
import { Box, TextField, Autocomplete } from '@mui/material';
import * as yup from 'yup';
import 'yup-phone';
import { FormControl } from '../onboarding/Onboarding.styled';
import { useForm } from '../../hooks/useForm';
import {
  useGetViewer,
  useUpdateUser,
  useGetIndustries,
} from '../../api/api.hooks';
import { Loading } from '../../components/loading/Loading';
import { states } from '../../api/api.constants';

const validationSchema = yup.object({
  firstName: yup.string().required('This field is required!'),
  lastName: yup.string().required('This field is required!'),
  phone: yup
    .string()
    .phone(
      'US',
      false,
      'Invalid phone number. Make sure it contains the country code!'
    )
    .required('This field is required!'),
  companyName: yup.string().required('This field is required!'),
  sector: yup.number().required('This field is required!'),
  state: yup.string().required('This field is required!'),
  zip: yup
    .string()
    .matches(/^\d{5}$/, 'Invalid zip code!')
    .required('This field is required!'),
});

export interface ProfileFormHandle {
  submitForm: () => Promise<unknown>;
}
export interface ProfileFormProps {
  onSuccess?: () => void;
  onError?: () => void;
  onLoading?: React.Dispatch<React.SetStateAction<boolean>>;
  onValidate?: React.Dispatch<React.SetStateAction<boolean>>;
  validateOnLoad?: boolean;
  completeOnboarding?: boolean;
}

export const ProfileForm = React.forwardRef<
  ProfileFormHandle,
  ProfileFormProps
>(
  (
    {
      onSuccess,
      onError,
      onLoading,
      onValidate,
      validateOnLoad,
      completeOnboarding,
    },
    ref
  ) => {
    const { data: viewer, isLoading: viewerLoading } = useGetViewer();
    const { data: industries, isLoading: industriesLoading } =
      useGetIndustries();

    const { mutate: updateViewer, status } = useUpdateUser();

    // define form
    const {
      values,
      touched,
      errors,
      isValid,
      handleChange,
      setValues,
      setFieldValue,
      setFieldTouched,
      submitForm,
    } = useForm({
      initialValues: {
        firstName: '',
        lastName: '',
        phone: '',
        companyName: '',
        sector: '',
        state: '',
        zip: '',
      },
      validationSchema,
      validateOnMount: true,
      onSubmit: (data) => {
        if (isValid && viewer) {
          updateViewer({
            id: viewer.id,
            first_name: data.firstName || null,
            last_name: data.lastName || null,
            phone_number: data.phone || null,
            company_name: data.companyName || null,
            company_sector: Number(data.sector) || null,
            company_state: data.state || null,
            company_zip_code: data.zip || null,
            onboarding_completed: completeOnboarding ? 1 : undefined,
          });
        }
      },
    });

    // expose imperative submitForm
    useImperativeHandle(
      ref,
      () => ({
        submitForm,
      }),
      [submitForm]
    );

    // trigger events
    useEffect(() => {
      onLoading?.(status === 'loading' || viewerLoading || industriesLoading);
    }, [onLoading, status, viewerLoading, industriesLoading]);

    useEffect(() => {
      onValidate?.(isValid);
    }, [onValidate, isValid]);

    useEffect(() => {
      if (status === 'success') {
        onSuccess?.();
      } else if (status === 'error') {
        onError?.();
      }
    }, [onError, onSuccess, status]);

    // fill data from viewer
    useEffect(() => {
      if (viewer) {
        setValues(
          {
            firstName: viewer.first_name || '',
            lastName: viewer.last_name || '',
            phone: viewer.phone_number || '',
            companyName: viewer.company_name || '',
            sector: viewer.company_sector?.toString() || '',
            state: viewer.company_state || '',
            zip: viewer.company_zip_code || '',
          },
          true
        );
      }
    }, [setValues, viewer]);

    if (viewerLoading || industriesLoading) {
      return <Loading />;
    }

    return (
      <>
        <Box display="flex" gap={2} mb={1}>
          <Box
            display="flex"
            flexShrink={0}
            justifyContent="end"
            width={48}
            mt={2}
          >
            <BadgeTwoTone />
          </Box>
          <Box display="flex" flexGrow={1} gap={2}>
            <FormControl>
              <TextField
                size="small"
                name="firstName"
                label="First Name"
                error={
                  (validateOnLoad || touched.firstName) &&
                  Boolean(errors.firstName)
                }
                value={values.firstName}
                onChange={handleChange}
                helperText={
                  (validateOnLoad || touched.firstName) && errors.firstName
                }
              />
            </FormControl>
            <FormControl inline>
              <TextField
                size="small"
                name="lastName"
                label="Last Name"
                error={
                  (validateOnLoad || touched.lastName) &&
                  Boolean(errors.lastName)
                }
                value={values.lastName}
                onChange={handleChange}
                helperText={
                  (validateOnLoad || touched.lastName) && errors.lastName
                }
              />
            </FormControl>
          </Box>
        </Box>

        <Box display="flex" gap={2} mb={1}>
          <Box
            display="flex"
            flexShrink={0}
            justifyContent="end"
            width={48}
            mt={2}
          >
            <PhoneTwoTone />
          </Box>
          <Box flexGrow={1}>
            <FormControl>
              <TextField
                size="small"
                name="phone"
                label="Mobile Number"
                error={
                  (validateOnLoad || touched.phone) && Boolean(errors.phone)
                }
                value={values.phone}
                onChange={handleChange}
                helperText={(validateOnLoad || touched.phone) && errors.phone}
              />
            </FormControl>
          </Box>
        </Box>

        <Box display="flex" gap={2} mb={1}>
          <Box
            display="flex"
            flexShrink={0}
            justifyContent="end"
            width={48}
            mt={2}
          >
            <BusinessTwoTone />
          </Box>
          <Box flexGrow={1}>
            <FormControl>
              <TextField
                size="small"
                name="companyName"
                label="Company Name"
                value={values.companyName}
                onChange={handleChange}
              />
            </FormControl>
          </Box>
        </Box>

        <Box display="flex" gap={2} mb={1}>
          <Box display="flex" justifyContent="end" width={48} mt={2}>
            <MiscellaneousServicesTwoTone />
          </Box>
          <Box flexGrow={1}>
            <FormControl>
              <Autocomplete
                disablePortal
                autoHighlight
                fullWidth
                value={values.sector?.toString() || ''}
                onChange={(event: unknown, newValue: string | null) => {
                  setFieldTouched('sector');
                  setFieldValue('sector', newValue || '', true);
                }}
                options={
                  industries?.map((i) => i.value.toString()).concat('') || []
                }
                getOptionLabel={(o) =>
                  industries?.find((i) => i.value.toString() === o)?.text || ''
                }
                renderInput={(params) => (
                  <TextField
                    {...params}
                    name="sector"
                    sx={{
                      input: {
                        fontSize: 14,
                      },
                    }}
                    fullWidth
                    margin="none"
                    size="small"
                    label="Sector"
                    error={
                      (validateOnLoad || touched.sector) &&
                      Boolean(errors.sector)
                    }
                    helperText={
                      (validateOnLoad || touched.sector) && errors.sector
                    }
                  />
                )}
              />
            </FormControl>
          </Box>
        </Box>

        <Box display="flex" gap={2} mb={1}>
          <Box display="flex" justifyContent="end" width={48} mt={2}>
            <AddLocationTwoTone />
          </Box>
          <Box flexGrow={1}>
            <FormControl>
              <Autocomplete
                disablePortal
                autoHighlight
                fullWidth
                value={values.state || ''}
                onChange={(event: unknown, newValue: string | null) => {
                  setFieldTouched('state');
                  setFieldValue('state', newValue || '', true);
                }}
                options={Object.keys(states)}
                getOptionLabel={(o) => (o.length ? states[o] : '')}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    name="state"
                    sx={{
                      input: {
                        fontSize: 14,
                      },
                    }}
                    fullWidth
                    margin="none"
                    size="small"
                    label="State"
                    error={
                      (validateOnLoad || touched.state) && Boolean(errors.state)
                    }
                    helperText={
                      (validateOnLoad || touched.state) && errors.state
                    }
                  />
                )}
              />
            </FormControl>
          </Box>
        </Box>

        <Box display="flex" gap={2} mb={2}>
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
                name="zip"
                label="Zip Code"
                error={(validateOnLoad || touched.zip) && Boolean(errors.zip)}
                value={values.zip}
                onChange={handleChange}
                helperText={(validateOnLoad || touched.zip) && errors.zip}
              />
            </FormControl>
          </Box>
        </Box>
      </>
    );
  }
);
