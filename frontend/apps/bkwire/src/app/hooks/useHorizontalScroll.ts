import { useEffect, useState } from 'react';

export const useHorizontalScroll = () => {
  const [element, setElement] = useState<HTMLDivElement>();

  useEffect(() => {
    if (element) {
      const onWheel = (e: WheelEvent) => {
        if (e.deltaY !== 0 && element.clientWidth < element.scrollWidth) {
          e.preventDefault();

          element.scrollTo({
            left: element.scrollLeft + e.deltaY * 4,
            behavior: 'smooth',
          });
        }
      };

      element.addEventListener('wheel', onWheel);

      return () => element.removeEventListener('wheel', onWheel);
    }

    return undefined;
  }, [element]);

  return setElement;
};
