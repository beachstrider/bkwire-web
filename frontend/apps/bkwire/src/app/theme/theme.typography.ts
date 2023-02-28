import { Theme } from '@mui/material';
import { TypographyOptions } from '@mui/material/styles/createTypography';

declare module '@mui/material/styles' {
  interface TypographyVariants {
    greeting: React.CSSProperties;
    subtitle: React.CSSProperties;
    verticalLabel: React.CSSProperties;
    horizontalLabel: React.CSSProperties;
    body3: React.CSSProperties;
  }

  interface TypographyVariantsOptions {
    greeting?: React.CSSProperties;
    subtitle?: React.CSSProperties;
    verticalLabel?: React.CSSProperties;
    horizontalLabel?: React.CSSProperties;
    body3?: React.CSSProperties;
  }
}

declare module '@mui/material/Typography' {
  interface TypographyPropsVariantOverrides {
    greeting: true;
    subtitle: true;
    verticalLabel: true;
    horizontalLabel: true;
    body3: true;
    subtitle1: false;
    subtitle2: false;
    h4: false;
    h5: false;
    h6: false;
  }
}

const getTypography = (theme: Theme): TypographyOptions => ({
  fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  htmlFontSize: 16,
  fontSize: 14,
  fontWeightLight: 300,
  fontWeightRegular: 400,
  fontWeightMedium: 500,
  fontWeightBold: 700,
  greeting: {
    fontWeight: 400,
    fontSize: '2.5rem',
    lineHeight: 1.167,
    letterSpacing: '0em',
  },
  subtitle: {
    fontWeight: 400,
    fontSize: '1rem',
    lineHeight: 1.75,
    letterSpacing: '0.00938em',
    display: 'block',
    color: '#7392cb',
  },
  h1: {
    fontWeight: 400,
    fontSize: '2.125rem',
    lineHeight: 1.235,
    letterSpacing: '0.00735em',
    minHeight: 42,
    marginTop: 24,
    marginBottom: 24,
    color: '#010066',
  },
  h2: {
    fontWeight: 500,
    fontSize: '1.2rem',
    lineHeight: 1.1,
    letterSpacing: '0.0075em',
    color: '#010066',
  },
  h3: {
    fontWeight: 400,
    fontSize: '1.1rem',
    lineHeight: 1.05,
    letterSpacing: '0em',
    color: '#7392cb',
  },
  body1: {
    fontWeight: 400,
    fontSize: '1rem',
    lineHeight: 'initial',
    letterSpacing: '0.00938em',
  },
  body2: {
    fontWeight: 400,
    fontSize: '0.875rem',
    lineHeight: '17px',
    letterSpacing: '0.01071em',
    minHeight: 17,
  },
  body3: {
    fontWeight: 400,
    fontSize: '0.75rem',
    lineHeight: 'normal',
    letterSpacing: '0.03333em',
  },
  verticalLabel: {
    fontWeight: 400,
    fontSize: '0.75rem',
    lineHeight: 1.66,
    letterSpacing: '0.03333em',
    display: 'block',
    transform: 'rotate(-90deg)',
    textAlign: 'center',
    alignSelf: 'center',
  },
  horizontalLabel: {
    fontWeight: 400,
    fontSize: '0.75rem',
    lineHeight: 1.66,
    letterSpacing: '0.03333em',
  },
  button: {
    fontWeight: 500,
    fontSize: '0.875rem',
    lineHeight: 1.75,
    letterSpacing: '0.02857em',
    textTransform: 'none',
  },
  caption: {
    fontWeight: 400,
    fontSize: '0.75rem',
    lineHeight: '14px',
    letterSpacing: '0.03333em',
    color: theme.palette.grey[500],
    minHeight: 14,
  },
  overline: {
    fontWeight: 400,
    fontSize: '0.75rem',
    lineHeight: 2.66,
    letterSpacing: '0.08333em',
    textTransform: 'uppercase',
  },
});

export default getTypography;
