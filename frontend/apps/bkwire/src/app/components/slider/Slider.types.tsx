export type SliderEvent =
  | React.MouseEvent<HTMLDivElement, MouseEvent>
  | React.TouchEvent<HTMLDivElement>;

export interface ResponsivePeekConfig {
  breakpoint?: number;
  minWidth: number;
  maxWidth: number;
  minPeekWidth: number;
  mlr: number;
  transitionDuration: number;
  showPagination: boolean;
  showControls: boolean;
}

export interface ResponsiveControlsConfig {
  breakpoint?: number;
  itemsPerPage: number;
  transitionDuration: number;
  showPagination: boolean;
  showControls: boolean;
}

export type ResponsiveMode = 'peek' | 'controls';
export type ResponsiveConfig = ResponsivePeekConfig | ResponsiveControlsConfig;

export interface Layout {
  responsive: ResponsiveConfig;
  responsiveMode: ResponsiveMode;
  pageWidth: number;
  peekWidth: number;
  itemWidth: number;
  itemsPerPage: number;
  blankWidth: number;
  pages: number[][];
}

export interface SliderPaginationPosition {
  top?: number;
  left?: number;
  bottom?: number;
  right?: number;
}

export interface SliderProps {
  minHeight?: number;
  /** the space between items */
  gap?: number | string;
  /** min drag length to be considered a swipe */
  swipeThreshold?: number;
  /** enable mouse touch simulation */
  mouseSimulatesTouch?: boolean;
  /** responsive configuration with 'controls' or 'peek' modes */
  responsive?: ResponsiveConfig[];
  loading?: boolean;
  /** card component to be used as a skeleton while loading the items */
  cardSkeleton?: React.FC;
  /** card component to be used when there are no items in the slider */
  emptyCard?: React.FC;
  /** absolute x position of the controls */
  controlsPosition?: number;
  /** absolute position of the pagination */
  paginationPosition?: SliderPaginationPosition;
  /** auto change slide delay */
  autoplay?: number;
}

export interface Vector2 {
  x: number;
  y: number;
}
