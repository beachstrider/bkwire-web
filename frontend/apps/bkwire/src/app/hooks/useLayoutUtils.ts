import { useTheme } from '@mui/material';
import { useCallback } from 'react';

export enum Elem {
  Header = 1 << 0,
  HeaderTall = 1 << 1,
  Heading = 1 << 2,
  PageTabs = 1 << 3,
  Footer = 1 << 4,
}

export const useLayoutUtils = () => {
  const theme = useTheme();

  const computeHeight = useCallback(
    (elements: Elem) => {
      let height = 0;

      if ((elements & Elem.Header) !== 0) {
        height += theme.layout.headerHeight;
      } else if ((elements & Elem.HeaderTall) !== 0) {
        height += theme.layout.headerTallHeight;
      }

      if ((elements & Elem.Heading) !== 0) {
        height +=
          Number(theme.typography.h1.minHeight) +
          Number(theme.typography.h1.marginTop) +
          Number(theme.typography.h1.marginBottom) +
          theme.layout.gutter;
      }

      if ((elements & Elem.PageTabs) !== 0) {
        height += theme.layout.pageTabsHeight + theme.layout.gutter;
      }

      if ((elements & Elem.Footer) !== 0) {
        height += theme.layout.footerHeight;
      }

      return height;
    },
    [
      theme.layout.footerHeight,
      theme.layout.gutter,
      theme.layout.headerHeight,
      theme.layout.headerTallHeight,
      theme.layout.pageTabsHeight,
      theme.typography.h1.marginBottom,
      theme.typography.h1.marginTop,
      theme.typography.h1.minHeight,
    ]
  );

  const fillHeightCss = useCallback(
    (elements: Elem, extraSpace = 0) =>
      `calc(100vh - ${computeHeight(
        elements
      )}px - ${extraSpace} * ${theme.spacing(1)})`,
    [computeHeight, theme]
  );

  return { computeHeight, fillHeightCss };
};
