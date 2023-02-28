import { ArrowBackIosNew, ArrowForwardIos } from '@mui/icons-material';
import _clamp from 'lodash/clamp';
import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  SliderPagination,
  SliderRoot,
  SliderViewport,
  SliderPages,
  SliderPage,
  SliderControl,
  SliderPaginationPage,
} from './Slider.styled';
import { useClientRect } from '../../hooks/useClientRect';
import { SliderProps, Vector2 } from './Slider.types';
import { useSliderLayout, useSliderTouch } from './Slider.hooks';

const defaultLayout = [
  {
    itemsPerPage: 1,
    transitionDuration: 300,
    showPagination: true,
    showControls: false,
  },
];

export const Slider = ({
  minHeight = 0,
  gap = 0,
  swipeThreshold = 60,
  mouseSimulatesTouch = false,
  responsive = defaultLayout,
  autoplay = 0,
  controlsPosition = -56,
  paginationPosition,
  loading,
  cardSkeleton: CardSkeleton,
  emptyCard: EmptyCard,
  children,
}: SliderProps & { children: React.ReactNode[] }) => {
  const items = React.Children.toArray(children);

  const sliderContent = useRef<HTMLDivElement | null>(null);
  const containerRef = useRef(null);
  const rect = useClientRect(containerRef);

  const [transitionEnabled, setTransitionEnabled] = useState(false);
  const [scrolling, setScrolling] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);

  const onLayoutChanged = useCallback(() => {
    setTransitionEnabled(false);
  }, [setTransitionEnabled]);

  const { layout, getOffsetX } = useSliderLayout(
    rect.width,
    items.length,
    responsive,
    loading,
    onLayoutChanged
  );

  const setPosition = (dragOffset: Vector2) => {
    if (sliderContent.current) {
      const offsetX = loading ? 0 : getOffsetX(currentPage, dragOffset.x);
      sliderContent.current.style.transform = `translateX(${offsetX}px)`;
    }
  };

  const navigatePageInDirection = useCallback(
    (direction: number) => {
      if (loading) {
        return;
      }

      let pageIndex = _clamp(currentPage, 0, layout.pages.length - 1);
      pageIndex += direction;
      if (pageIndex < 0) pageIndex = layout.pages.length - 1;
      if (pageIndex > layout.pages.length - 1) pageIndex = 0;

      setTransitionEnabled(true);

      setCurrentPage(pageIndex);

      setScrolling(true);
      setTimeout(
        () => setScrolling(false),
        layout.responsive.transitionDuration
      );
    },
    [
      currentPage,
      layout.pages.length,
      layout.responsive.transitionDuration,
      loading,
    ]
  );

  const navigatePage = useCallback(
    (page: number) => {
      if (loading) {
        return;
      }

      const pageIndex = _clamp(page, 0, layout.pages.length - 1);

      setTransitionEnabled(true);

      setCurrentPage(pageIndex);

      setScrolling(true);
      setTimeout(
        () => setScrolling(false),
        layout.responsive.transitionDuration
      );
    },
    [layout.pages.length, layout.responsive.transitionDuration, loading]
  );

  const { touchHandlers, mouseHandlers, dragDelta } = useSliderTouch({
    currentPage,
    pageCount: layout.pages.length,
    swipeThreshold,
    onSwipe: navigatePageInDirection,
    onDragging: setPosition,
    onTouchStart: () => setTransitionEnabled(false),
    onTouchEnd: () => setTransitionEnabled(true),
  });

  // reset current page index when items change
  useEffect(() => {
    setCurrentPage(0);
  }, [items.length]);

  // setup autoplay
  useEffect(() => {
    const intervalId =
      autoplay > 0
        ? setInterval(() => {
            navigatePageInDirection(1);
          }, autoplay)
        : null;

    return () => {
      if (intervalId !== null) {
        clearInterval(intervalId);
      }
    };
  }, [autoplay, navigatePageInDirection]);

  setPosition(dragDelta);

  return (
    <SliderRoot ref={containerRef} minHeight={minHeight}>
      <SliderViewport>
        <SliderPages
          ref={sliderContent}
          transition={transitionEnabled}
          transitionDuration={layout.responsive.transitionDuration}
          {...touchHandlers}
          {...(mouseSimulatesTouch ? { ...mouseHandlers } : {})}
        >
          {layout.pages.map((page) => (
            <SliderPage
              key={page[0]}
              width={page.length * layout.itemWidth}
              minHeight={minHeight}
              gap={gap}
              blankWidth={layout.blankWidth}
            >
              {page.map((itemIndex) =>
                loading
                  ? CardSkeleton && <CardSkeleton key={itemIndex} />
                  : !items.length
                  ? EmptyCard && <EmptyCard key={itemIndex} />
                  : items[itemIndex]
              )}
            </SliderPage>
          ))}
        </SliderPages>
      </SliderViewport>

      {layout.responsiveMode === 'controls' &&
        layout.responsive.showControls &&
        items.length > layout.itemsPerPage && (
          <>
            {currentPage !== 0 && (
              <SliderControl
                align="left"
                variant="contained"
                color="primary"
                position={controlsPosition}
                endIcon={<ArrowBackIosNew />}
                onClick={() => navigatePageInDirection(-1)}
                disabled={scrolling}
              />
            )}

            <SliderControl
              align="right"
              variant="contained"
              color="primary"
              position={controlsPosition}
              endIcon={<ArrowForwardIos />}
              onClick={() => navigatePageInDirection(1)}
              disabled={scrolling}
            />
          </>
        )}

      {layout.responsive.showPagination && (
        <SliderPagination {...paginationPosition}>
          {layout.pages.map((page, pageIndex) => (
            <SliderPaginationPage
              key={page[0]}
              active={pageIndex === currentPage}
              onClick={() => navigatePage(pageIndex)}
            />
          ))}
        </SliderPagination>
      )}
    </SliderRoot>
  );
};
