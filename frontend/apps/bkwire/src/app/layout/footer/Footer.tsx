import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Mail, Phone } from '@mui/icons-material';
import {
  Box,
  Button,
  Container,
  Dialog,
  DialogActions,
  Typography,
  useTheme,
} from '@mui/material';
import { FooterRoot } from './Footer.styled';
import { ButtonLink } from '../../components/ButtonLink';
import { useAuth0 } from '@auth0/auth0-react';
import { useGetViewer, useUpdateUser } from '../../api/api.hooks';
import { Loading } from '../../components/loading/Loading';
import {
  PolicyTypes,
  policyTypes,
  useGetPolicies,
} from '../../hooks/useGetPolicies';

const icons: Record<string, React.ReactNode> = {
  Phone: <Phone />,
  Mail: <Mail />,
};

export const Footer = () => {
  const theme = useTheme();
  const policies = useGetPolicies();
  const { loginWithRedirect } = useAuth0();
  const { isLoading: isAuthLoading } = useAuth0();
  const { data: viewer, isLoading: isViewerLoading } = useGetViewer();
  const { mutate: updateViewer, status } = useUpdateUser();

  const [isTOCOpen, setTOCOpen] = useState(false);
  const [tocRef, setTOCRef] = useState<HTMLDivElement | null>(null);

  const openTOC = useCallback(() => setTOCOpen(true), []);

  const handleTOCClose = useCallback(
    (reason: string) => {
      if (viewer) {
        if (viewer.tos) {
          setTOCOpen(false);
        } else if (reason === 'agree') {
          updateViewer({
            id: viewer.id,
            tos: 1,
          });
          setTOCOpen(false);
        }
      }
    },
    [updateViewer, viewer]
  );

  useEffect(() => {
    tocRef
      ?.querySelector('.MuiDialog-paper')
      ?.scroll({ top: 0, behavior: 'auto' });
  }, [tocRef]);

  useEffect(() => {
    if (viewer && !viewer.tos) {
      setTOCOpen(true);
    }
  }, [viewer]);

  const links: {
    header: string;
    links: {
      name: string;
      href?: string;
      onClick?: () => void;
      icon?: string;
      disabled?: boolean;
    }[];
  }[] = useMemo(
    () => [
      {
        header: 'About',
        links: [
          { name: 'FAQ', href: '', disabled: true },
          { name: 'Company', href: '', disabled: true },
          //{ name: 'Blog', href: '', disabled: true },
          //{ name: 'Careers', href: '', disabled: true },
        ],
      },
      {
        header: 'Product',
        links: [
          { name: 'Pricing plans', href: '/account/billing' },
          /*
          {
            name: 'Features',
            onClick: () =>
              document.getElementById('features')?.scrollIntoView(),
            disabled: true,
          },
          {
            name: 'Why BK Wire',
            onClick: () =>
              document.getElementById('why-bkwire')?.scrollIntoView(),
            disabled: true,
          },
          {
            name: 'Sign up today',
            onClick: () => loginWithRedirect({ screen_hint: 'signup' }),
            disabled: true,
          },
          {
            name: 'Sign in',
            onClick: () => loginWithRedirect(),
            disabled: true,
          },
          */
        ],
      },
      {
        header: 'Resources',
        links: [
        //  { name: 'Corporate bankruptcies', href: '/list/bankruptcies' },
        //  { name: 'Corporate losses', href: '/list/losses' },
          { name: 'Terms of service', onClick: () => openTOC() },
          { name: 'Privacy policy', onClick: () => openTOC() },
          { name: 'Chapter Types', onClick: () => openTOC() },
        //  { name: 'Security', href: '', disabled: true },
        ],
      },
      {
        header: 'Contact',
        links: [
          {
            name: '816-596-9978',
            href: '',
            icon: 'Phone',
          },
          {
            name: 'support@bkwire.com',
            href: '',
            icon: 'Mail',
          },
        ],
      },
    ],
    [loginWithRedirect, openTOC]
  );

  return (
    <FooterRoot component="footer" height={theme.layout.footerHeight}>
      <Container maxWidth="lg">
        <Box display="flex" flexDirection="column" flexGrow={1}>
          <Box display="flex" flexDirection="row">
            <Box className="logo" />
            {!isAuthLoading &&
              !isViewerLoading &&
              links.map((col) => (
                <Box className="links-col" key={col.header}>
                  <Typography variant="body2" fontWeight="bold">
                    {col.header}
                  </Typography>
                  {col.links.map((link) => (
                    <ButtonLink
                      className={`link ${link.disabled ? 'disabled' : ''}`}
                      key={link.name}
                      to={link.href}
                      onClick={link.onClick}
                      disabled={link.disabled}
                    >
                      {!!link.icon && icons[link.icon]}
                      {link.name}
                    </ButtonLink>
                  ))}
                </Box>
              ))}
          </Box>
          <Typography className="copyright" variant="body2">
            {`© ${new Date().getFullYear()} BKwire. All rights reserved.`}
          </Typography>
        </Box>
      </Container>

      <Dialog
        open={isTOCOpen}
        maxWidth="md"
        onClose={(_, reason) => handleTOCClose(reason)}
        ref={setTOCRef}
      >
        {!policies ? (
          <Box p={4}>
            <Loading />
          </Box>
        ) : (
          <Box p={4} id="policy">
            <div>
              By using the BKwire services or content, you agree to the BKwire
              Terms of Service, Disclaimer, Privacy Policy, EULA, Cookie Policy
              and Consent Tool found here.
            </div>

            <h2>About the Service</h2>

            <p>
              BKwire provides real time information regarding corporate
              bankruptcies, compiled from public sources such as the Public
              Access to Court Electronic Records (PACER) system and presented in
              a user-friendly format. Available data includes debtors,
              creditors, claim amounts (“business impacts”) and other docket
              data. When requested, email or other notifications are provided of
              new bankruptcy cases, updates to existing cases, and/or other
              related data. BKwire endeavors to include up to date, accurate and
              complete bankruptcy data; however, because we rely on public
              sources such as PACER, it is possible that errors, omissions,
              delays, unavailability, or other issues with the source data may
              result in errors, omissions, delays or other issues to the data
              presented on the BKwire website or within the BKwire email
              notifications. BKwire makes no warranties or representations about
              the services or content provided, including but not limited to its
              accuracy, reliability, completeness, or timeliness.
            </p>
            <p>
              As provided in the BKwire Terms of Service (below), the services
              and content are provided on an “as is” and “as available” basis,
              without warranty of any kind, express or implied, including, but
              not limited to, implied warranties of merchantability,
              completeness, fitness for a particular purpose, or
              non-infringement. BKwire is not liable for the truth, accuracy, or
              completeness of any information provided, or for errors, mistakes,
              omissions, delays or interruptions of data from whatever cause.
              You agree you use the services and content at your own risk and
              BKwire is not liable for any damages of any kind arising from or
              relating to the use of or reliance on the data presented on the
              BKwire website.
            </p>

            {policyTypes.map((p) => (
              <React.Fragment key={p}>
                <hr />
                <div
                  dangerouslySetInnerHTML={{
                    __html: policies[p as PolicyTypes],
                  }}
                />
              </React.Fragment>
            ))}
          </Box>
        )}

        <DialogActions sx={{ p: 4, pt: 0 }}>
          {Boolean(viewer?.tos) && (
            <Button
              variant="outlined"
              color="primary"
              onClick={() => handleTOCClose('close')}
            >
              Close
            </Button>
          )}
          <Button
            variant="contained"
            color="primary"
            disabled={!policies}
            onClick={() => handleTOCClose('agree')}
            autoFocus
          >
            Agree
          </Button>
        </DialogActions>
      </Dialog>
    </FooterRoot>
  );
};
