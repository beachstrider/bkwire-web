import { css } from '@mui/system';

export const nonAttr = (...props: string[]) => ({
  shouldForwardProp: (p: string) => props.indexOf(p) === -1,
});

export const vignetteCss = (size: number, opacity: number) => css`
  &::after {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    content: '';
    box-shadow: 0 0 ${size}px rgba(0, 0, 0, ${opacity}) inset;
  }
`;
