import { useCallback, useEffect, useState } from 'react';
import _debounce from 'lodash/debounce';

export const useDebounce = <T>(target: T, delay: number) => {
  const [debouncedValue, setValue] = useState<T>(target);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const setDebouncedValue = useCallback(_debounce(setValue, delay), []);

  useEffect(() => {
    setDebouncedValue(target);
  }, [target, setDebouncedValue]);

  return debouncedValue;
};
