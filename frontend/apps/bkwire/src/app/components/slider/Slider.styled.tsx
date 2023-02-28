import { Button, styled } from '@mui/material';
import { nonAttr } from '../../utils/styled';
import { SliderPaginationPosition } from './Slider.types';

export const SliderRoot = styled('div', nonAttr('minHeight'))<{
  minHeight: number;
}>`
  display: flex;
  justify-content: center;
  min-height: ${(p) => p.minHeight}px;
  touch-action: pan-y !important;

  * {
    user-select: none !important;
    -webkit-user-drag: none !important;
    -moz-user-drag: none !important;
  }
`;

export const SliderViewport = styled('div')`
  overflow: hidden;
  padding: 10px 0;
`;

export const SliderPages = styled(
  'div',
  nonAttr('transition', 'transitionDuration')
)<{
  transition: boolean;
  transitionDuration: number;
}>`
  transition: ${(p) =>
    p.transition ? `transform ${p.transitionDuration}ms ease-out` : 'none'};

  display: flex;
  width: max-content;
  overflow: visible;
  left: 0;
  transform: translateX(0);
`;

export const SliderPage = styled(
  'div',
  nonAttr('width', 'minHeight', 'blankWidth', 'gap')
)<{
  width: number;
  minHeight: number;
  blankWidth: number;
  gap: number | string;
}>`
  width: ${(p) => p.width}px;
  min-height: ${(p) => p.minHeight}px;
  margin-right: ${(p) => p.blankWidth}px;

  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: 1fr;
  align-items: stretch;

  > * {
    margin: 0 ${(p) => `${p.gap}${typeof p.gap === 'string' ? '' : 'px'}`};
    overflow: hidden;
    width: auto;
  }
`;

export const SliderControl = styled(Button, nonAttr('align', 'position'))<{
  align: 'left' | 'right';
  position: number;
}>`
  ${(p) => p.align}: ${(p) => p.position}px;

  position: absolute;
  min-width: auto;
  z-index: 2;
  align-self: center;
  background-color: black;
  border-color: black;
  border-radius: 30px;
  padding: 0;
  color: white;
  transition-duration: 0ms;

  .MuiButton-endIcon {
    margin: 0;
    padding: ${(p) => p.theme.spacing(1)};

    svg {
      font-size: 14px;
      transform: translateX(${(p) => (p.align === 'left' ? -1 : 1)}px);
    }
  }
`;

export const SliderPagination = styled(
  'div',
  nonAttr('top', 'left', 'bottom', 'right')
)<SliderPaginationPosition>`
  position: absolute;
  bottom: 0px;
  ${(p) => (p.top !== undefined ? `top: ${p.top}px;` : '')}
  ${(p) => (p.left !== undefined ? `left: ${p.left}px;` : '')}
  ${(p) => (p.bottom !== undefined ? `bottom: ${p.bottom}px;` : '')}
  ${(p) => (p.right !== undefined ? `right: ${p.right}px;` : '')}
`;

export const SliderPaginationPage = styled('div', nonAttr('active'))<{
  active: boolean;
}>`
  background: ${(p) => (p.active ? 'black' : p.theme.palette.grey[200])};
  border: 1px solid black;
  border-radius: 6px;

  float: left;
  width: 12px;
  height: 12px;
  margin: 4px;
  cursor: pointer;

  &:first-of-type {
    margin-left: 0;
  }
  &:last-of-type {
    margin-right: 0;
  }
`;
