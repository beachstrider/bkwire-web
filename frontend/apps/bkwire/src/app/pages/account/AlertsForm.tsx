import React, { useState, useEffect, useImperativeHandle } from 'react';
import {
  Box,
  FormLabel,
  IconButton,
  Switch,
  TextField,
  Typography,
} from '@mui/material';
import Close from '@mui/icons-material/Close';
import * as yup from 'yup';
import { useForm } from '../../hooks/useForm';
import { ButtonLink } from '../../components/ButtonLink';
import { FormControl } from '../onboarding/Onboarding.styled';
import { useUpdateUser } from '../../api/api.hooks';
import { User } from '../../api/api.types';

const validationSchema = yup.object({
  emails: yup.array(
    yup.object({
      email: yup
        .string()
        .email('Please enter a valid email!')
        .required('This field is required!'),
    })
  ),
  phones: yup.array(
    yup.object({
      phone: yup
        .string()
        .matches(/^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$/im, {
          message: 'Please enter a valid phone number!',
          excludeEmptyString: true,
        })
        .required('This field is required!'),
    })
  ),
});

interface FormData {
  emails: { email: string }[];
  phones: { phone: string }[];
}
export interface AlertsFormHandle {
  submitForm: () => Promise<unknown>;
}
export interface AlertFormProps {
  viewer: User;
  setIsFormValid: React.Dispatch<React.SetStateAction<boolean>>;
  onLoading?: () => void;
  onSuccess?: () => void;
  onError?: () => void;
  reorder?: boolean;
}

export const AlertsForm = React.forwardRef<AlertsFormHandle, AlertFormProps>(
  ({ viewer, setIsFormValid, onLoading, onSuccess, onError, reorder }, ref) => {
    const [emailAlertsEnabled, setEmailAlertsEnabled] = useState(
      viewer.email_alerts_enabled
    );
    const [textAlertsEnabled, setTextAlertsEnabled] = useState(
      viewer.text_alerts_enabled
    );
    const [newsletter, setNewsletter] = useState<'daily' | 'weekly'>(
      viewer.daily ? 'daily' : viewer.weekly ? 'weekly' : 'weekly'
    );
    const { mutate: updateViewerAlerts, status } = useUpdateUser();

    const showAdditionalInputs =
      viewer.subscription_price_level > 1 &&
      viewer.subscription_status === 'active';

    // define form
    const {
      values,
      setValues,
      errors,
      handleChange,
      addField,
      removeField,
      getFieldMeta,
      submitForm,
    } = useForm<FormData>({
      initialValues: {
        emails: [
          { email: viewer.email_alert_1 },
          { email: viewer.email_alert_2 },
        ].filter((e) => !!e.email) as { email: string }[],
        phones: [
          { phone: viewer.phone_alert_1 },
          { phone: viewer.phone_alert_2 },
        ].filter((e) => !!e.phone) as { phone: string }[],
      },
      validationSchema,
      // validateOnMount: true,
      onSubmit: (data) => {
        updateViewerAlerts({
          id: viewer.id,
          email_alerts_enabled: emailAlertsEnabled,
          email_alert_1: !showAdditionalInputs
            ? null
            : data.emails[0]?.email || null,
          email_alert_2: !showAdditionalInputs
            ? null
            : data.emails[1]?.email || null,
          text_alerts_enabled: textAlertsEnabled,
          phone_alert_1: !showAdditionalInputs
            ? null
            : data.phones[0]?.phone || null,
          phone_alert_2: !showAdditionalInputs
            ? null
            : data.phones[1]?.phone || null,
          daily: Number(newsletter === 'daily'),
          weekly: Number(newsletter === 'weekly'),
        });
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
      if (status === 'loading') {
        onLoading?.();
      }
      if (status === 'success') {
        onSuccess?.();
      } else if (status === 'error') {
        onError?.();
      }
    }, [status, onError, onLoading, onSuccess]);

    // set values from viewer
    useEffect(() => {
      setValues(
        {
          emails: emailAlertsEnabled ? values.emails : [],
          phones: textAlertsEnabled ? values.phones : [],
        },
        true
      );
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [emailAlertsEnabled, textAlertsEnabled]);

    // validate
    useEffect(() => {
      setIsFormValid(
        (!emailAlertsEnabled || !errors.emails?.length) &&
          (!textAlertsEnabled || !errors.phones?.length)
      );
    }, [
      emailAlertsEnabled,
      textAlertsEnabled,
      errors.emails?.length,
      errors.phones?.length,
      setIsFormValid,
      values.emails?.length,
      values.phones?.length,
    ]);

    return (
      <>
        <Box display="flex" gap={2} p={4}>
          <Box width={48}>
            <Switch
              checked={Boolean(emailAlertsEnabled)}
              onChange={() => setEmailAlertsEnabled((p) => Number(!p))}
            />
          </Box>
          <Box flexGrow={1} pt="3px">
            <Typography variant="h3" mb={1}>
              Send notifications by email
            </Typography>

            <Typography variant="body2" fontWeight="bold">
              Immediately Reduce Your Companies Risk By Receiving Critical
              Corporate Bankruptcies and Businesses Impacted Notifications
            </Typography>

            {Boolean(emailAlertsEnabled) && showAdditionalInputs && (
              <Box mt={2} mb={1} flexGrow={1}>
                {values.emails.map((value, index) => {
                  const path = `emails[${index}].email`;
                  const { error, touched } = getFieldMeta(path);

                  return (
                    <FormControl key={`email-${index}`}>
                      <IconButton
                        className="remove-btn"
                        onClick={removeField('emails', index)}
                      >
                        <Close />
                      </IconButton>

                      <TextField
                        size="small"
                        name={path}
                        label="Email"
                        error={touched && Boolean(error)}
                        value={value.email}
                        onChange={handleChange}
                        helperText={touched && error}
                      />
                    </FormControl>
                  );
                })}
                {showAdditionalInputs && values.emails.length < 2 && (
                  <ButtonLink onClick={addField('emails', { email: '' })}>
                    Add an additional notification email
                  </ButtonLink>
                )}
              </Box>
            )}
          </Box>
        </Box>

        <Box display="flex" gap={2} p={4} order={reorder ? 1 : 0}>
          <Box width={48}>
            <Switch
              checked={Boolean(textAlertsEnabled)}
              onChange={() => setTextAlertsEnabled((p) => Number(!p))}
            />
          </Box>
          <Box flexGrow={1} pt="3px">
            <Typography variant="h3" mb={1}>
              Send notifications by text message
            </Typography>

            <Typography variant="body2" fontWeight="bold">
              BKwire receives the most updated corporate bankruptcy information.
            </Typography>
            <Typography variant="body2" fontWeight="bold">
              BKwire will only text you for Breaking Corporate Bankruptcy News.
            </Typography>

            {Boolean(textAlertsEnabled) && showAdditionalInputs && (
              <Box mt={2} mb={1} flexGrow={1}>
                {values.phones.map((value, index) => {
                  const path = `phones[${index}].phone`;
                  const { error, touched } = getFieldMeta(path);

                  return (
                    <FormControl key={`phone-${index}`}>
                      <IconButton
                        className="remove-btn"
                        onClick={removeField('phones', index)}
                      >
                        <Close />
                      </IconButton>

                      <TextField
                        size="small"
                        name={path}
                        label="Phone"
                        error={touched && Boolean(error)}
                        value={value.phone}
                        onChange={handleChange}
                        helperText={touched && error}
                      />
                    </FormControl>
                  );
                })}
                {values.phones.length < 2 && (
                  <ButtonLink onClick={addField('phones', { phone: '' })}>
                    Add an additional mobile number
                  </ButtonLink>
                )}
              </Box>
            )}
          </Box>
        </Box>

        <Box
          px={4}
          pb={0}
          display={emailAlertsEnabled || textAlertsEnabled ? 'block' : 'none'}
        >
          <FormControl>
            <FormLabel
              sx={{
                display: 'flex',
                gap: 2,
                alignItems: 'center',
                cursor: 'pointer',
              }}
            >
              <Switch
                checked={newsletter === 'daily'}
                onChange={(e) => e.target.checked && setNewsletter('daily')}
              />
              <Typography variant="h3">
                Receive daily updates (most popular)
              </Typography>
            </FormLabel>
          </FormControl>
          <FormControl>
            <FormLabel
              sx={{
                display: 'flex',
                gap: 2,
                alignItems: 'center',
                cursor: 'pointer',
              }}
            >
              <Switch
                checked={newsletter === 'weekly'}
                onChange={(e) => e.target.checked && setNewsletter('weekly')}
              />
              <Typography variant="h3">Receive weekly updates</Typography>
            </FormLabel>
          </FormControl>
        </Box>
      </>
    );
  }
);
