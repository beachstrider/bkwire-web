import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';

export const useScrollToTop = () => {
  const location = useLocation();
  const prevPathname = useRef<string>();

  useEffect(() => {
    if (location.pathname !== prevPathname.current) {
      prevPathname.current = location.pathname;
      window.scrollTo(0, 0);
    }
  }, [location]);
};
