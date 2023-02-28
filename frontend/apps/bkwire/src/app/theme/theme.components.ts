import { Theme } from '@mui/material';
import type { } from '@mui/x-data-grid/themeAugmentation';

declare module '@mui/material/Button' {
  interface ButtonPropsVariantOverrides {
    link: true;
  }
}

const getComponents = (theme: Theme) => ({
  MuiButtonBase: {
    defaultProps: {
      disableRipple: true,
    },
  },
  MuiButton: {
    variants: [
      {
        props: { variant: 'link' },
        style: {
          justifyContent: 'start',
          textTransform: 'none',
          border: 'none',
          color: theme.palette.link.main,
          fontWeight: 'normal',
          minWidth: 'unset',
          padding: 0,
          margin: 0,
          '&:hover': {
            backgroundColor: 'transparent',
            textDecoration: 'underline',
          },
          '.MuiButton-endIcon': {
            marginTop: -2,
          },
        },
      },
    ],
    styleOverrides: {
      // variant: text, outlined, contained
      // color: primary, secondary, error, warning, success, info
      // Ex:
      // containedPrimary: {
      //   '&:hover': {
      //     color: 'black',
      //     backgroundColor: 'gray',
      //   },
      // },
    },
  },
  MuiSwitch: {
    styleOverrides: {
      root: {
        width: 48,
        height: 24,
        padding: 0,
        transform: 'scale(0.8)',
        '& .MuiSwitch-switchBase': {
          padding: 1,
          margin: 2,
          transitionDuration: '200ms',
          '&.Mui-checked': {
            transform: 'translateX(24px)',
            color: 'white',
            '& + .MuiSwitch-track': {
              backgroundColor: theme.palette.success.main,
              opacity: 1,
              border: 0,
            },
            '&.Mui-disabled + .MuiSwitch-track': {
              opacity: 0.7,
            },
          },
          '&.Mui-disabled .MuiSwitch-thumb': {
            color: theme.palette.grey[300],
          },
          '&.Mui-disabled + .MuiSwitch-track': {
            opacity: 1,
          },
        },
        '& .MuiSwitch-thumb': {
          boxSizing: 'border-box',
          width: 18,
          height: 18,
        },
        '& .MuiSwitch-track': {
          borderRadius: 40,
          backgroundColor: theme.palette.grey[500],
          opacity: 1,
          transition: theme.transitions.create(['background-color'], {
            duration: 400,
          }),
        },
      },
    },
  },
  MuiDataGrid: {
    styleOverrides: {
      root: {
        backgroundColor: 'white',
        border: 'none',
        borderRadius: 0,
        '*': { outline: 'none !important' },
        // '.MuiDataGrid-footerContainer': {
        //   position: 'relative',
        //   '::after': {
        //     content: '""',
        //     position: 'absolute',
        //     top: '-40px',
        //     width: 'calc(100% - 17px)',
        //     height: '40px',
        //     background: 'rgba(255, 255, 255, 0.5)',
        //   },
        // },
        '.rest-row': {
          backgroundColor: '#f1f1f1',
        }
      },
      columnHeaders: {
        borderRadius: 0,
        backgroundColor: '#e3e3e3',
        '.MuiDataGrid-columnHeader--sorted': {
          backgroundColor: '#ccc',
        },
      },
      iconSeparator: {
        color: 'transparent',
      },
      cell: {
        borderColor: '#e3e3e3',
        paddingLeft: 10,
        paddingRight: 10,
      },
    },
  },
});

export default getComponents;
