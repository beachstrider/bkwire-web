import { matchPath, resolvePath, useLocation } from 'react-router-dom';

export const useRouteUtils = () => {
  const location = useLocation();

  const matchArea = (area: string) =>
    !!matchPath(`/${area}/*`, location.pathname);

  const matchPage = (page: string) =>
    !!matchPath(
      resolvePath(`../${page}`, location.pathname).pathname,
      location.pathname
    );

  const matchAreas = (areas: string[]) => areas.map(matchArea);
  const matchPages = (pages: string[]) => pages.map(matchPage);

  return {
    matchArea,
    matchPage,
    matchAreas,
    matchPages,
  };
};
