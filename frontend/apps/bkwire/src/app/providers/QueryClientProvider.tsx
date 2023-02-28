import React from 'react';
import {
  QueryClient,
  QueryClientProvider as ReactQueryClienProvider,
} from 'react-query';
// import { ReactQueryDevtools } from 'react-query/devtools';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: true,
      refetchOnMount: true,
      refetchOnReconnect: true,
      retry: true,
      staleTime: 5 * 60 * 1000,
    },
  },
});

export const QueryClientProvider: React.FC = ({ children }) => (
  <ReactQueryClienProvider client={queryClient}>
    {children}
    {/* <ReactQueryDevtools initialIsOpen={false} /> */}
  </ReactQueryClienProvider>
);

export default QueryClientProvider;
