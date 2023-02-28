import { useCallback, useEffect, useMemo } from 'react';
import { useLocation, useSearchParams } from 'react-router-dom';
import { isEqual } from 'lodash';

const SEPARATOR = ',';

export function useQueryStringState<T extends string | string[]>(
  key: string,
  initialValue: T,
  persist: 'none' | 'page' | 'app' = 'none',
  persistKey = ''
) {
  const [searchParams, setSearchParams] = useSearchParams();
  const { pathname } = useLocation();

  const lsKey =
    persist === 'page'
      ? `${persistKey}:${pathname}:${key}`
      : `${persistKey}:${key}`;
  const isArray = Array.isArray(initialValue);

  const stringifiedValue =
    searchParams.get(key) ||
    (persist !== 'none' ? localStorage.getItem(lsKey) : null) ||
    (isArray ? initialValue.join(SEPARATOR) : initialValue);

  if (persist !== 'none') {
    localStorage.setItem(lsKey, stringifiedValue);
  }

  useEffect(() => {
    const hasSearchKey = searchParams.has(key);

    if (!hasSearchKey || !isEqual(searchParams.get(key), stringifiedValue)) {
      searchParams.set(key, stringifiedValue);
      setSearchParams(searchParams, { replace: !hasSearchKey });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const value = isArray ? stringifiedValue.split(SEPARATOR) : stringifiedValue;

  const setValue = useCallback(
    (newValue: T, replace = false) => {
      const stringifiedNewValue = isArray
        ? (newValue as string[]).join(SEPARATOR)
        : (newValue as string);

      if (isEqual(searchParams.get(key), stringifiedNewValue)) {
        return;
      }

      if (!newValue.length) {
        searchParams.delete(key);
        localStorage.removeItem(lsKey);
      } else {
        searchParams.set(key, stringifiedNewValue);
      }

      setSearchParams(searchParams, { replace });
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [searchParams]
  );

  const result = useMemo(
    () => [value, setValue] as [T, (val: T, replace?: boolean) => void],
    [value, setValue]
  );

  return result;
}
