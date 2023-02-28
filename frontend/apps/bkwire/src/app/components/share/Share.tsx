import { Close } from '@mui/icons-material';
import {
  Box,
  Button,
  DialogActions,
  FormControl,
  IconButton,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material';
import React, { useImperativeHandle } from 'react';
import { useCallback, useState } from 'react';
import { ShareRoot } from './Share.styled';
import * as yup from 'yup';
import { useForm } from '../../hooks/useForm';
import LinkIcon from '@mui/icons-material/Link';
import MailOutlineIcon from '@mui/icons-material/MailOutline';
import useApi from '../../api/api.client';
import { useSnackbar } from 'notistack';

const validationSchema = yup.object({
  email: yup
    .string()
    .email('Please enter a valid email!')
    .required('This field is required!'),
  comment: yup.string(),
});

export type ShareHandle = {
  open: (url: string, id: string, type: 'bk' | 'loss') => void;
  close: () => void;
};

export const Share = React.forwardRef<ShareHandle, unknown>((_, ref) => {
  const { get } = useApi();
  const { enqueueSnackbar } = useSnackbar();

  const [isModalOpen, setModalOpen] = useState(false);
  const [tab, setTab] = useState(0);
  const [showComment, setShowComment] = useState(false);
  const [url, setUrl] = useState('');
  const [id, setId] = useState('');
  const [type, setType] = useState('bk');

  const open = useCallback(
    (url: string, id: string, type: 'bk' | 'loss') => {
      setUrl(url);
      setId(id);
      setType(type);
      setModalOpen(true);
    },
    [setModalOpen]
  );

  const close = useCallback(() => {
    setModalOpen(false);
  }, [setModalOpen]);

  useImperativeHandle(
    ref,
    () => ({
      open,
      close,
    }),
    [open, close]
  );

  const copyUrl = useCallback(() => {
    navigator.clipboard.writeText(url);
    enqueueSnackbar('The url was copied to your clipboard!', {
      variant: 'success',
    });
    close();
  }, [close, url, enqueueSnackbar]);

  const { values, touched, errors, setFieldValue, handleChange, handleSubmit } =
    useForm({
      initialValues: {
        email: '',
        comment: '',
      },
      validationSchema,
      validateOnMount: true,
      onSubmit: () => {
        const comment =
          (showComment && encodeURIComponent(values.comment)) || '';
        if (type === 'bk') {
          get(
            `/share-case?email_address=${values.email}&dcid=${id}&comment=${comment}`
          );
        } else {
          get(
            `/share-loss?email_address=${values.email}&lossid=${id}&comment=${comment}`
          );
        }
        setFieldValue('email', '');
        setFieldValue('comment', '');
        setModalOpen(false);
      },
    });

  return (
    <ShareRoot open={isModalOpen} onClose={close}>
      <IconButton className="modal-close" onClick={close}>
        <Close />
      </IconButton>
      <Box display="flex" flexDirection="column">
        <Box className="modal-header">
          <Typography variant="h1" mb={0}>
            {type === 'bk'
              ? 'Share Corporate Bankruptcy'
              : 'Share Impacted Business'}
          </Typography>
          <Tabs value={tab} onChange={(_, t) => setTab(t)}>
            <Tab label="URL" icon={<LinkIcon />} iconPosition="start" />
            <Tab
              label="Email"
              icon={<MailOutlineIcon />}
              iconPosition="start"
            />
          </Tabs>
        </Box>
        <Box className="modal-body">
          <Box className="modal-body-panel" hidden={tab !== 0}>
            <Typography variant="h3">Copy this link to share:</Typography>
            <FormControl>
              <TextField size="small" name="url" value={url} />
            </FormControl>
            <DialogActions>
              <Button variant="contained" size="large" onClick={copyUrl}>
                Copy
              </Button>
            </DialogActions>
          </Box>
          <Box className="modal-body-panel" hidden={tab !== 1}>
            <Typography variant="h3">Email a link to share:</Typography>
            <FormControl>
              <TextField
                size="small"
                name="email"
                placeholder="Email"
                error={touched.email && Boolean(errors.email)}
                value={values.email}
                onChange={handleChange}
                helperText={touched.email && errors.email}
              />
            </FormControl>
            {showComment && (
              <FormControl>
                <TextField
                  size="small"
                  name="comment"
                  placeholder="Add a comment..."
                  multiline
                  rows={3}
                  error={touched.comment && Boolean(errors.comment)}
                  value={values.comment}
                  onChange={handleChange}
                  helperText={touched.comment && errors.comment}
                />
              </FormControl>
            )}
            <Button variant="link" onClick={() => setShowComment((p) => !p)}>
              {showComment ? 'Remove comment' : 'Add a comment'}
            </Button>
            <DialogActions>
              <Button
                variant="contained"
                size="large"
                onClick={() => handleSubmit()}
              >
                Send
              </Button>
            </DialogActions>
          </Box>
        </Box>
      </Box>
    </ShareRoot>
  );
});
