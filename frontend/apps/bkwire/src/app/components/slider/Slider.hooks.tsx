import _clamp from 'lodash/clamp';
import React, { useState, useEffect, useRef } from 'react';
import {
  Layout,
  ResponsiveConfig,
  ResponsiveControlsConfig,
  ResponsiveMode,
  ResponsivePeekConfig,
  SliderEvent,
  Vector2,
} from './Slider.types';

export const useSliderLayout = (
  width: number,
  childCount: number,
  responsive: ResponsiveConfig[],
  loading?: boolean,
  onLayoutChanged?: () => void
) => {
  const [layout, setLayout] = useState<Layout>({
    responsive: responsive[0],
    responsiveMode: 'controls',
    pageWidth: 0,
    peekWidth: 0,
    itemWidth: 0,
    itemsPerPage: 0,
    blankWidth: 0,
    pages: [],
  });

  useEffect(() => {
    const responsiveConfig =
      responsive.find(
        (c) => c.breakpoint === undefined || c.breakpoint > width
      ) || responsive[responsive.length - 1];

    let pageWidth: number;
    let peekWidth: number;
    let itemWidth: number;
    let itemsPerPage: number;
    let blankWidth: number;
    let responsiveMode: ResponsiveMode;

    const peekConfig = responsiveConfig as ResponsivePeekConfig;
    if (peekConfig.minWidth !== undefined) {
      responsiveMode = 'peek';

      // start with min widths for items and peek
      let peekSpace = peekConfig.minPeekWidth * 2;
      itemWidth = peekConfig.minWidth;

      pageWidth = width - peekSpace;
      itemsPerPage = Math.max(Math.floor(pageWidth / itemWidth), 1);

      const remainingSpace = pageWidth - itemsPerPage * itemWidth;

      // divide the remaining space amongst items and peek
      // items must not be stretched beyond maxWidth
      const itemStretchWidth = Math.min(
        remainingSpace / (itemsPerPage + 1),
        peekConfig.maxWidth - peekConfig.minWidth
      );
      itemWidth += itemStretchWidth;

      // peek gets all the remaining space
      const peekStretchWidth = remainingSpace - itemStretchWidth * itemsPerPage;
      peekSpace += peekStretchWidth;

      // page width must be recomputed because peek space was stretched
      pageWidth = width - peekSpace;

      peekWidth = peekSpace / 2;

      blankWidth = 0;

      // if there is only one page, fill the remaining space with blank space
      // so that child count does not affect the layout
      if (!loading && childCount <= itemsPerPage) {
        peekWidth = 0;
        blankWidth =
          (itemsPerPage - childCount) * itemWidth +
          peekSpace -
          peekConfig.mlr * 2;
      }
    } else {
      responsiveMode = 'controls';

      const controlsConfig = responsiveConfig as ResponsiveControlsConfig;

      itemsPerPage = controlsConfig.itemsPerPage;
      pageWidth = width;
      peekWidth = 0;
      itemWidth = pageWidth / itemsPerPage;

      blankWidth = 0;

      // if there is only one page, fill the remaining space with blank space
      // so that child count does not affect the layout
      if (!loading && childCount <= itemsPerPage) {
        peekWidth = 0;
        blankWidth = (itemsPerPage - childCount) * itemWidth;
      }
    }

    // generate page indices array
    // if loading, add a full page of skeletons plus a second page with one skeleton
    // for empty result sets, add a page with a single empty card
    const itemCount = loading ? itemsPerPage + 1 : Math.max(childCount, 1);
    const pageCount = Math.ceil(itemCount / itemsPerPage);
    const pages: number[][] = [];
    for (let pageIndex = 0; pageIndex < pageCount; pageIndex++) {
      const itemIndices: number[] = [];

      for (let index = 0; index < itemsPerPage; index++) {
        const itemIndex = pageIndex * itemsPerPage + index;

        if (itemIndex < itemCount) {
          itemIndices.push(itemIndex);
        }
      }

      pages.push(itemIndices);
    }

    setLayout({
      responsive: responsiveConfig,
      responsiveMode,
      pageWidth,
      peekWidth,
      itemWidth,
      itemsPerPage,
      blankWidth,
      pages,
    });

    if (onLayoutChanged) {
      onLayoutChanged();
    }
  }, [childCount, width, responsive, loading, onLayoutChanged]);

  const getOffsetX = (page: number, dragOffsetX: number) => {
    const pageIndex = loading ? 0 : _clamp(page, 0, layout.pages.length - 1);

    const mlr =
      layout.responsiveMode === 'peek'
        ? (layout.responsive as ResponsivePeekConfig).mlr
        : 0;

    let offsetX = 0;

    if (pageIndex === 0) {
      offsetX += mlr; // first page does not peek left
    } else {
      offsetX += layout.peekWidth;
    }

    if (pageIndex === layout.pages.length - 1) {
      offsetX += layout.peekWidth - mlr; // last page does not peek right
    }

    if (layout.pages.length) {
      for (let i = 1; i <= pageIndex; i++) {
        offsetX -= layout.pages[i].length * layout.itemWidth;
      }
    }

    return offsetX + dragOffsetX;
  };

  return { layout, getOffsetX };
};

export const useSliderTouch = ({
  currentPage,
  pageCount,
  swipeThreshold,
  onSwipe,
  onDragging,
  onTouchStart,
  onTouchEnd,
}: {
  currentPage: number;
  pageCount: number;
  swipeThreshold: number;
  onSwipe: (direction: 1 | -1) => void;
  onDragging: (position: Vector2) => void;
  onTouchStart?: () => void;
  onTouchEnd?: () => void;
}) => {
  const dragging = useRef(false);
  const dragStart = useRef<Vector2>({ x: 0, y: 0 });
  const dragDelta = useRef<Vector2>({ x: 0, y: 0 });
  const dragAnimationId = useRef<number>(-1);

  const sliderScroll = useRef<boolean | undefined>(undefined);

  const getTouchPosition = (e: SliderEvent): Vector2 => {
    const mouseEvent = e as React.MouseEvent<HTMLDivElement, MouseEvent>;
    const touchEvent = e as React.TouchEvent<HTMLDivElement>;

    return {
      x: mouseEvent?.pageX ?? touchEvent.touches[0].clientX,
      y: mouseEvent?.pageY ?? touchEvent.touches[0].clientY,
    };
  };

  const dragAnimation = () => {
    onDragging(dragDelta.current);

    if (dragging.current) {
      dragAnimationId.current = requestAnimationFrame(dragAnimation);
    }
  };

  const touchStartHandler = (e: SliderEvent) => {
    dragStart.current = getTouchPosition(e);
    dragDelta.current = { x: 0, y: 0 };
    dragging.current = true;

    sliderScroll.current = undefined;

    if (onTouchStart) {
      onTouchStart();
    }

    dragAnimationId.current = requestAnimationFrame(dragAnimation);
  };

  const touchMoveHandler = (e: SliderEvent) => {
    if (dragging.current) {
      const touchPosition = getTouchPosition(e);

      let dx = touchPosition.x - dragStart.current.x;
      let dy = touchPosition.y - dragStart.current.y;

      if (sliderScroll.current === undefined) {
        // sliderScroll is set to undefined by touchStartHandler.
        // this means that this is the first touch move event.
        // we here decide if we should capture the scroll event for the slider
        // or not, based on the direction of the touch.
        sliderScroll.current = Math.abs(dx) > Math.abs(dy);
      }

      if (sliderScroll.current) {
        dy = 0;
      } else {
        dx = 0;
      }

      dragDelta.current = {
        x: dx,
        y: dy,
      };
    }
  };

  const touchEndHandler = () => {
    if (dragging.current) {
      dragging.current = false;
      cancelAnimationFrame(dragAnimationId.current);

      sliderScroll.current = undefined;

      if (onTouchEnd) {
        onTouchEnd();
      }

      if (
        dragDelta.current.x < -swipeThreshold &&
        currentPage < pageCount - 1
      ) {
        onSwipe(1);
      } else if (dragDelta.current.x > swipeThreshold && currentPage > 0) {
        onSwipe(-1);
      } else {
        onDragging({ x: 0, y: 0 });
      }

      dragDelta.current = { x: 0, y: 0 };
    }
  };

  return {
    touchHandlers: {
      onTouchStart: touchStartHandler,
      onTouchMove: touchMoveHandler,
      onTouchEnd: touchEndHandler,
    },
    mouseHandlers: {
      onMouseDown: touchStartHandler,
      onMouseMove: touchMoveHandler,
      onMouseUp: touchEndHandler,
      onMouseLeave: touchEndHandler,
    },
    dragDelta: dragDelta.current,
  };
};
