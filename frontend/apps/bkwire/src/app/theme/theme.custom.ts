import { Theme, ThemeOptions } from '@mui/material';

declare module '@mui/material/styles' {
  interface Theme {
    layout: {
      headerHeight: number;
      headerTallHeight: number;
      footerHeight: number;
      pageTabsHeight: number;
      gutter: number;
    };
    textHighlightShadow: string;
    pagePaperShadow: string;
  }

  interface ThemeOptions {
    layout?: {
      headerHeight?: number;
      headerTallHeight?: number;
      footerHeight?: number;
      pageTabsHeight?: number;
      gutter?: number;
    };
    textHighlightShadow?: string;
    pagePaperShadow?: string;
  }
}

// layout
const getCustom = (theme: Theme): ThemeOptions => ({
  layout: {
    headerHeight: 64,
    headerTallHeight: 100,
    footerHeight: 300,
    pageTabsHeight: 48,
    gutter: 16,
  },
  textHighlightShadow: `
    #fff2 0px 0px 2px,
    #fff2 0px 0px 3px,
    #fff2 0px 0px 5px,
    #fff2 0px 0px 7px,
    #fff2 0px 0px 10px,
    #fff2 0px 0px 12px,
    #fff2 0px 0px 14px,
    #fff2 0px 0px 22px
  `,
  pagePaperShadow: `
    0px 2px 4px -1px rgba(0,0,0,0.04),
    0px 1px 10px 0px rgba(0,0,0,0.04),
    0px 1px 3px 0px rgba(0,0,0,0.04)
  `,
});

export default getCustom;
