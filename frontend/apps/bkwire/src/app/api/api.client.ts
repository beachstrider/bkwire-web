import { useAuth0 } from '@auth0/auth0-react';
import axios, { Axios, AxiosRequestConfig } from 'axios';
import qs from 'qs';

const instance = axios.create({
  baseURL: process.env.NX_API_URL,
  headers: { 'Content-Type': 'application/json' },
  paramsSerializer: (params) => qs.stringify(params, { indices: false }),
});

const useApi = () => {
  const { getAccessTokenSilently } = useAuth0();

  const withAuthHeader = async <D = unknown>(
    config?: AxiosRequestConfig<D>
  ) => ({
    ...config,
    headers: {
      ...(config?.headers || {}),
      Authorization: `Bearer ${await getAccessTokenSilently({
        ignoreCache: false,
      })}`,
    },
  });

  const withUrlEncodedHeader = <D = unknown>(
    config?: AxiosRequestConfig<D>
  ) => ({
    ...config,
    headers: {
      ...(config?.headers || {}),
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  const api: Axios & {
    postUrlEncoded: typeof instance.post;
    getNoAuth: typeof instance.get;
  } = {
    ...instance,
    getUri: instance.getUri,
    request: instance.request,
    options: instance.options,

    getNoAuth: async (url, config) => instance.get(url, config),
    get: async (url, config) => instance.get(url, await withAuthHeader(config)),
    post: async (url, data, config) =>
      instance.post(url, data, await withAuthHeader(config)),

    postUrlEncoded: async (url, data, config) =>
      instance.post(
        url,
        qs.stringify(data, { indices: false }) as unknown,
        await withAuthHeader(withUrlEncodedHeader(config))
      ),

    put: async (url, data, config) =>
      instance.put(url, data, await withAuthHeader(config)),
    patch: async (url, data, config) =>
      instance.patch(url, data, await withAuthHeader(config)),
    delete: async (url, config) =>
      instance.delete(url, await withAuthHeader(config)),
    head: async (url, config) =>
      instance.head(url, await withAuthHeader(config)),
  };
  return api;
};

export default useApi;
