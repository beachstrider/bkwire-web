import { Theme, lighten, darken, alpha } from '@mui/material';

declare module '@mui/material/styles' {
  interface Palette {
    link: Palette['primary'];
  }
  interface PaletteOptions {
    link: PaletteOptions['primary'];
  }
  interface Palette {
    brand: Palette['primary'];
  }
  interface PaletteOptions {
    brand: PaletteOptions['primary'];
  }
}

const brandColor = 'rgb(1, 1, 102)';

const getPalette = (theme: Theme) => ({
  mode: 'light',

  contrastThreshold: 3,
  tonalOffset: 0.2,

  brand: {
    main: brandColor,
    light: lighten(brandColor, 10),
    dark: darken(brandColor, 10),
    contrastText: '#fff',
  },
  primary: {
    main: '#010066',
    light: '#111',
    dark: '#010066',
    contrastText: '#fff',
  },
  secondary: {
    main: '#ffa000',
    light: 'rgb(255, 179, 51)',
    dark: 'rgb(178, 112, 0)',
    contrastText: '#010066',
  },
  link: {
    main: '#06B',
    light: '#07C',
    dark: '#05A',
    contrastText: '#fff',
  },

  info: {
    main: '#eee',
    light: '#fff',
    dark: '#ddd',
    contrastText: '#010066',
  },
  error: {
    main: '#d32f2f',
    light: '#ef5350',
    dark: '#c62828',
    contrastText: '#fff',
  },
  warning: {
    main: '#ed6c02',
    light: '#ff9800',
    dark: '#e65100',
    contrastText: '#fff',
  },
  success: {
    main: '#2e7d32',
    light: '#4caf50',
    dark: '#1b5e20',
    contrastText: '#fff',
  },

  text: {
    primary: alpha(brandColor, 0.87),
    secondary: alpha(brandColor, 0.6),
    disabled: alpha(brandColor, 0.38),
  },

  background: {
    paper: '#fff',
    default: '#fff',
  },

  divider: alpha('#fff', 0.12),

  action: {
    active: alpha(brandColor, 0.54),
    hover: alpha(brandColor, 0.04),
    hoverOpacity: 0.04,
    selected: alpha(brandColor, 0.08),
    selectedOpacity: 0.08,
    disabled: alpha(brandColor, 0.26),
    disabledBackground: alpha(brandColor, 0.12),
    disabledOpacity: 0.38,
    focus: alpha(brandColor, 0.12),
    focusOpacity: 0.12,
    activatedOpacity: 0.12,
  },
});

export default getPalette;
