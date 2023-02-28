import {
  RefObject,
  useLayoutEffect,
  useRef,
  useCallback,
  useState,
} from 'react';

interface ClientRect {
  x: number;
  y: number;
  width: number;
  height: number;
  top: number;
  right: number;
  bottom: number;
  left: number;
}

export const useClientRect = <T extends HTMLElement>(
  elementRef: RefObject<T>
): ClientRect => {
  const [clientRect, setClientRect] = useState<ClientRect>({
    x: 0,
    y: 0,
    width: 0,
    height: 0,
    top: 0,
    right: 0,
    bottom: 0,
    left: 0,
  });

  const observer = useRef<IntersectionObserver | null>(null);

  const handleResize = useCallback(() => {
    if (elementRef?.current) {
      const rect = elementRef.current.getBoundingClientRect().toJSON();

      setClientRect(rect);

      // NOTE: the window can be resized when the element is hidden so it gets a zero rect.
      // when the element is visible again, we want to set the correct clientRect.
      if (!observer.current && (rect.width === 0 || rect.height === 0)) {
        new IntersectionObserver((entries, o) => {
          observer.current = o;
          const isVisible = entries.some((e) => e.intersectionRatio > 0);
          if (isVisible) {
            handleResize();
            o.disconnect();
            observer.current = null;
          }
        }).observe(elementRef.current);
      }
    }
  }, [elementRef]);

  useLayoutEffect(() => {
    handleResize();
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (observer.current) {
        observer.current.disconnect();
        observer.current = null;
      }
    };
  }, [elementRef, handleResize]);

  return clientRect;
};
