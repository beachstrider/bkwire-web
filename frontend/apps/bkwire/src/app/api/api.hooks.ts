import {
  BankruptcyFilters,
  BankruptcySorting,
  LossFilters,
  LossSorting,
  NotificationRecord,
  BankruptcyDetails,
  Industry,
  SearchResult,
  User,
  News,
  Docket,
  City,
  NotificationType,
  NotificationStatus,
  BankruptciesResult,
  LossesResult,
  SplashItem,
  DocketFile,
  UserFileAccess,
} from './api.types';
import { QueryKey, useMutation, useQuery, useQueryClient } from 'react-query';
import { SelectMatrixOption } from '../components/selectMatrix/SelectMatrix.types';
import useApi from './api.client';
import { useAuth0 } from '@auth0/auth0-react';
import { TRIAL_DAYS, industryIcons } from './api.constants';
import { format, differenceInDays } from 'date-fns';
import { useSnackbar } from 'notistack';
import { useCallback } from 'react';

// NOTE: use this for optimistic results accross multiple query key variants
const useUpdateQueryData = <TPrevData, TParams>({
  queryKey,
  updater,
}: {
  queryKey: QueryKey;
  updater: (prevData: TPrevData, params: TParams) => void;
}) => {
  const client = useQueryClient();
  return (params: TParams) => {
    const cache = client.getQueryCache();
    cache
      .findAll(queryKey)
      .forEach((query) =>
        client.setQueryData(query.queryKey, (prevData: unknown) =>
          updater(prevData as TPrevData, params)
        )
      );
  };
};

export const useGetIndustries = () => {
  const { get } = useApi();

  return useQuery<SelectMatrixOption[], Error>('query-industries', async () => {
    const { data } = await get<Industry[]>('/industries');

    return data.map((i) => ({
      value: i.id,
      text: i.naics_desc,
      icon: industryIcons[i.id],
    }));
  });
};

export const useGetCities = (state: string) => {
  const { get } = useApi();

  return useQuery<City[], Error>(['query-cities', state], async () => {
    const { data } = await get<City[]>('/list-cities', {
      params: { state_code: state },
    });
    return data.filter(
      (c, index) => data.findIndex((i) => i.city === c.city) === index
    );
  });
};

export const useGetViewer = () => {
  const { get } = useApi();
  const { user, isLoading } = useAuth0();

  return useQuery<User, Error>(
    ['query-viewer', isLoading],
    async () => {
      const { data } = await get<User>('/get-user', {
        params: { user_email: user?.email || '' },
      });
      const isSubscriptionActive = data.subscription_status === 'active';
      data.subscription =
        data.subscription_price_level === 3 && isSubscriptionActive
          ? 'mvp'
          : data.subscription_price_level === 2 && isSubscriptionActive
          ? 'team'
          : data.subscription_price_level === 1 && isSubscriptionActive
          ? 'individual'
          : differenceInDays(new Date(), new Date(data.date_added)) <=
            TRIAL_DAYS
          ? 'trial'
          : 'none';
      return data;
    },
    {
      enabled: !isLoading,
      keepPreviousData: true,
    }
  );
};

export const useUpdateUser = () => {
  const { post } = useApi();
  const queryClient = useQueryClient();

  return useMutation(
    async (user: Partial<User>) => {
      if (user.id === undefined) {
        return false;
      }
      await post('/update-user', user);
      return true;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['query-viewer']);
      },
    }
  );
};

export const useAddTeamMember = () => {
  const { post } = useApi();
  const queryClient = useQueryClient();

  return useMutation(
    async (email: string) => {
      const response = await post('/create-team-user', {
        member_email_address: email,
      });

      await queryClient.refetchQueries(['query-viewer']);
      return response;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['query-viewer']);
      },
    }
  );
};

export const useRemoveTeamMember = () => {
  const { post } = useApi();
  const queryClient = useQueryClient();

  return useMutation(
    async (email: string) => {
      const response = await post('/delete-team-user', {
        member_email_address: email,
      });

      await queryClient.refetchQueries(['query-viewer']);
      return response;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['query-viewer']);
      },
    }
  );
};

export const useChangePassword = () => {
  const { postUrlEncoded } = useApi();

  return useMutation(async (password: string) => {
    await postUrlEncoded('/change-password', { password });
    return true;
  });
};

export const useUpdateUserIndustries = () => {
  const { postUrlEncoded } = useApi();
  const queryClient = useQueryClient();

  return useMutation(
    async (update_industries: number[]) => {
      await postUrlEncoded('/update-user-industry', {
        update_industries: update_industries.join(','),
      });
      return true;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['query-viewer']);
      },
    }
  );
};

export const useGetDocket = (id: number) => {
  const { get } = useApi();

  return useQuery<Docket[], Error>(['query-docket', id], async () => {
    const { data } = await get<Docket[]>('/view-docket', {
      params: { id },
    });
    return data;
  });
};

export const useGetDocketFiles = (
  case_id?: number,
  docket_id?: number,
  doc_url?: string,
  docs_count = 0
) => {
  const { get } = useApi();

  return useQuery<DocketFile[], Error>(
    [
      'query-docket-files',
      {
        id: docket_id,
        dci_id: case_id,
        doc_url: doc_url,
      },
    ],
    async () => {
      const { data } = await get<DocketFile[]>('/file-link-get', {
        params: {
          dci_id: case_id,
          doc_url: doc_url,
          docket_entry_id: docket_id,
        },
      });
      return data;
    },
    {
      enabled: false,
      initialData:
        docs_count <= 1 && doc_url
          ? [
              {
                docket_link_id: 1,
                link: doc_url,
                filename: 'Main Document',
              },
            ]
          : [],
    }
  );
};

export const useGetUserFileAccess = (dci_id?: number) => {
  const { get } = useApi();

  return useQuery<UserFileAccess[], Error>(
    ['user-file-access', { dci_id }],
    async () => {
      const { data } = await get<UserFileAccess[]>('/get-user-file-access', {
        params: {
          dci_id,
        },
      });

      return data;
    },
    {
      enabled: false,
    }
  );
};

export const useCaseRefresh = (id: number) => {
  const { get } = useApi();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();

  const { data: viewer } = useGetViewer();

  const refresh = useCallback(async () => {
    if (!viewer || viewer.subscription !== 'mvp') {
      enqueueSnackbar('Need MVP access!', {
        variant: 'error',
      });
      return;
    }
    if (viewer.case_refresh_count >= viewer.case_refresh_max) {
      enqueueSnackbar('Max case refreshes exceeded!', {
        variant: 'error',
      });
      return;
    }

    await get('/case-refresh', {
      params: { dci_id: id },
    })
      .catch((e) => {
        enqueueSnackbar('Cannot refresh case. Please try again later!', {
          variant: 'error',
        });
      })
      .then(() => {
        queryClient.invalidateQueries(['query-viewer']); // for case_refresh_count

        enqueueSnackbar('You will be notified once the new data comes in!', {
          variant: 'success',
        });
      });
  }, [enqueueSnackbar, get, id, queryClient, viewer]);

  return refresh;
};

export const useSearch = (search: string, max_results: number) => {
  const { get } = useApi();

  return useQuery<SearchResult>(
    ['query-search', search, max_results],
    async () => {
      const { data } = await get<SearchResult>('/search', {
        params: {
          search,
          max_results,
        },
      });
      return data;
    },
    {
      enabled: !!search,
    }
  );
};

export const useGetBankruptcy = (id: number) => {
  const { get } = useApi();

  return useQuery<BankruptcyDetails, Error>(
    ['query-bankruptcy', { id }],
    async () => {
      const { data } = await get<BankruptcyDetails[]>('/view-bankruptcies', {
        params: { id },
      });
      return data[0] && { ...data[0], dci_id: id };
    }
  );
};

export const useGetBankruptcies = (
  page: number,
  pageSize: number,
  filters: BankruptcyFilters,
  industries: number[],
  sorting?: BankruptcySorting,
  search?: string,
  enabled = true
) => {
  const { get } = useApi();

  return useQuery<BankruptciesResult, Error>(
    [
      'query-bankruptcies',
      { page, pageSize, filters, industries, sorting, search },
    ],
    async () => {
      const { data } = await get<BankruptciesResult>('/list-bankruptcies', {
        params: {
          page,
          page_size: pageSize,
          sort_column: sorting?.field || 'date_added',
          sort_order: sorting?.sort || 'desc',
          search,
          chapter_types: filters.chapterTypes,
          asset_ranges: filters.assetRanges,
          liability_ranges: filters.liabilityRanges,
          industries: industries,
          start_date_added: filters.dateAdded[0]
            ? format(new Date(filters.dateAdded[0]), 'yyyy-MM-dd')
            : undefined,
          end_date_added: filters.dateAdded[1]
            ? format(new Date(filters.dateAdded[1]), 'yyyy-MM-dd')
            : undefined,
          start_date_filed: filters.dateFiled[0]
            ? format(new Date(filters.dateFiled[0]), 'yyyy-MM-dd')
            : undefined,
          end_date_filed: filters.dateFiled[1]
            ? format(new Date(filters.dateFiled[1]), 'yyyy-MM-dd')
            : undefined,
          state_code: filters.state || undefined,
          city: filters.city || undefined,
          involuntary: filters.involuntary,
          sub_chapv: filters.sub_chapv,
        },
      });
      return data;
    },
    {
      enabled,
    }
  );
};

export const useGetBankruptciesWatchlist = (
  page: number,
  pageSize: number,
  filters: BankruptcyFilters,
  sorting?: BankruptcySorting,
  search?: string
) => {
  const { get } = useApi();

  return useQuery<BankruptciesResult, Error>(
    [
      'query-bankruptcies-watchlist',
      { page, pageSize, filters, sorting, search },
    ],
    async () => {
      const { data } = await get<BankruptciesResult>(
        '/list-bankruptcies-watchlist',
        {
          params: {
            page,
            page_size: pageSize,
            sort_column: sorting?.field || 'date_added',
            sort_order: sorting?.sort || 'desc',
            search,
            chapter_types: filters.chapterTypes,
            asset_ranges: filters.assetRanges,
            liability_ranges: filters.liabilityRanges,
          },
        }
      );
      return data;
    }
  );
};

const watchlistedQueryBkUpdater = (
  prevData: BankruptciesResult | undefined,
  params: { id: number; watchlisted: boolean }
) => ({
  count: prevData?.count || 0,
  records: (prevData?.records || []).map((l) =>
    l.dci_id === params.id
      ? {
          ...l,
          is_bankruptcy_watchlisted: params.watchlisted ? 1 : 0,
        }
      : l
  ),
});

export const useAddToBankruptciesWatchlist = () => {
  const { post } = useApi();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();

  const updateQueryData = useUpdateQueryData({
    queryKey: 'query-bankruptcies',
    updater: watchlistedQueryBkUpdater,
  });

  return useMutation(
    async (id: number) => {
      await post('/add-to-bk-watchlist', { id });
      return true;
    },
    {
      onMutate: async (id) => {
        await queryClient.cancelQueries('query-bankruptcies');

        updateQueryData({ id, watchlisted: true });
      },
      onError: (_, id) => {
        updateQueryData({ id, watchlisted: false });
        enqueueSnackbar(
          'You cannot add any more bankruptcies to the watchlist at this time!',
          {
            variant: 'error',
          }
        );
      },
      onSettled: () => {
        queryClient.invalidateQueries();
      },
    }
  );
};

export const useRemoveFromBankruptciesWatchlist = () => {
  const { post } = useApi();
  const queryClient = useQueryClient();

  const updateQueryData = useUpdateQueryData({
    queryKey: 'query-bankruptcies',
    updater: watchlistedQueryBkUpdater,
  });

  const updateWatchlistRemoveQueryData = useUpdateQueryData({
    queryKey: 'query-bankruptcies-watchlist',
    updater: (
      prevData: BankruptciesResult | undefined,
      params: { id: number }
    ) => ({
      count: prevData?.count || 0,
      records: (prevData?.records || []).filter((l) => l.dci_id !== params.id),
    }),
  });

  return useMutation(
    async (id: number) => {
      await post('/remove-from-bk-watchlist', { id });
      return true;
    },
    {
      onMutate: async (id) => {
        await queryClient.cancelQueries('query-bankruptcies');
        await queryClient.cancelQueries('query-bankruptcies-watchlist');

        updateQueryData({ id, watchlisted: false });
        updateWatchlistRemoveQueryData({ id });
      },
      onError: (_, id) => {
        updateQueryData({ id, watchlisted: true });
      },
      onSettled: () => {
        queryClient.invalidateQueries();
      },
    }
  );
};

export const useGetCorporateLosses = (
  page: number,
  pageSize: number,
  filters: LossFilters,
  industries: number[],
  sorting?: LossSorting,
  search?: string,
  enabled = true
) => {
  const { get } = useApi();

  return useQuery<LossesResult, Error>(
    ['query-losses', { page, pageSize, filters, industries, sorting, search }],
    async () => {
      const { data } = await get<LossesResult>('/list-losses', {
        params: {
          page,
          page_size: pageSize,
          max_losses_per_case: filters.max_losses_per_case || undefined,
          sort_column: sorting?.field || 'date_added',
          sort_order: sorting?.sort || 'desc',
          search,
          loss: filters.loss || undefined,
          industries: industries,
          id: filters.id || undefined,
          start_date_filed: filters.dateFiled[0]
            ? format(new Date(filters.dateFiled[0]), 'yyyy-MM-dd')
            : undefined,
          end_date_filed: filters.dateFiled[1]
            ? format(new Date(filters.dateFiled[1]), 'yyyy-MM-dd')
            : undefined,
          start_date_added: filters.dateAdded[0]
            ? format(new Date(filters.dateAdded[0]), 'yyyy-MM-dd')
            : undefined,
          end_date_added: filters.dateAdded[1]
            ? format(new Date(filters.dateAdded[1]), 'yyyy-MM-dd')
            : undefined,
          state_code: filters.state || undefined,
          city: filters.city || undefined,
        },
      });
      return data;
    },
    {
      enabled,
    }
  );
};

export const useGetCompaniesWatchlist = (
  page: number,
  pageSize: number,
  filters: LossFilters,
  sorting?: LossSorting,
  search?: string
) => {
  const { get } = useApi();

  return useQuery<LossesResult, Error>(
    ['query-companies-watchlist', { page, pageSize, filters, sorting, search }],
    async () => {
      const { data } = await get<LossesResult>('/list-companies-watchlist', {
        params: {
          page,
          page_size: pageSize,
          sort_column: sorting?.field || 'date_added',
          sort_order: sorting?.sort || 'desc',
          search,
          loss: filters.loss || undefined,
          max_losses_per_case: filters.max_losses_per_case || undefined,
          id: filters.id || undefined,
        },
      });
      return data;
    }
  );
};

const watchlistedQueryLossesUpdater = (
  prevData: LossesResult | undefined,
  params: { id: number; watchlisted: boolean }
) => ({
  count: prevData?.count || 0,
  records: (prevData?.records || []).map((l) =>
    l.id === params.id
      ? {
          ...l,
          is_company_watchlisted: params.watchlisted ? 1 : 0,
        }
      : l
  ),
});

export const useAddToCompaniesWatchlist = () => {
  const { post } = useApi();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();

  const updateQueryData = useUpdateQueryData({
    queryKey: 'query-losses',
    updater: watchlistedQueryLossesUpdater,
  });

  return useMutation(
    async (id: number) => {
      await post('/add-to-companies-watchlist', { id });
      return true;
    },
    {
      onMutate: async (id) => {
        await queryClient.cancelQueries('query-losses');

        updateQueryData({ id, watchlisted: true });
      },
      onError: (_, id) => {
        updateQueryData({ id, watchlisted: false });
        enqueueSnackbar(
          'You cannot add any more companies to the watchlist at this time!',
          {
            variant: 'error',
          }
        );
      },
      onSettled: () => {
        queryClient.invalidateQueries();
      },
    }
  );
};

export const useRemoveFromCompaniesWatchlist = () => {
  const { post } = useApi();
  const queryClient = useQueryClient();

  const updateQueryData = useUpdateQueryData({
    queryKey: 'query-losses',
    updater: watchlistedQueryLossesUpdater,
  });

  const updateWatchlistRemoveQueryData = useUpdateQueryData({
    queryKey: 'query-companies-watchlist',
    updater: (prevData: LossesResult | undefined, params: { id: number }) => ({
      count: prevData?.count || 0,
      records: (prevData?.records || []).filter((l) => l.id !== params.id),
    }),
  });

  return useMutation(
    async (id: number) => {
      await post('/remove-from-companies-watchlist', { id });
      return true;
    },
    {
      onMutate: async (id) => {
        await queryClient.cancelQueries('query-losses');
        await queryClient.cancelQueries('query-companies-watchlist');

        updateQueryData({ id, watchlisted: false });
        updateWatchlistRemoveQueryData({ id });
      },
      onError: (_, id) => {
        updateQueryData({ id, watchlisted: true });
      },
      onSettled: () => {
        queryClient.invalidateQueries();
      },
    }
  );
};

export const useGetHistogram = () => {
  const { get } = useApi();

  return useQuery<{ days: number[]; lastDate: Date } | null, Error>(
    ['query-histogram'],
    async () => {
      const { data } = await get<{ count: number; date_filed: Date }[]>(
        '/bk-graph'
      );

      return data && data.length
        ? {
            days: data.map((d) => d.count),
            lastDate: new Date(data[data.length - 1].date_filed),
          }
        : null;
    },
    {
      // NOTE: refetch every minute
      refetchInterval: 60000,
    }
  );
};

export const useGetNews = (sector?: number) => {
  const { get } = useApi();

  return useQuery<News[], Error>(['query-news'], async () => {
    const { data } = await get<News[]>('/bk-news', {
      params: {
        industry: sector,
      },
    });
    return data;
  });
};

export const useGetUnreadNotifications = () => {
  const { get } = useApi();
  const queryClient = useQueryClient();

  return useQuery<number, Error>(
    ['query-unread-notifications'],
    async () => {
      const { data } = await get<NotificationRecord[]>('list-notifications', {
        params: {
          type: 'all',
          status: 'unread',
        },
      });

      const hasUnreadNotifications = data?.length ?? 0;

      if (hasUnreadNotifications) {
        // NOTE: invalidate case queries for case refresh success notifications
        const caseRefreshUnread = data.filter((n) => n.type === 'refresh_ok');
        caseRefreshUnread.forEach((n) => {
          queryClient.invalidateQueries(['query-viewer']); // for case_refresh_count
          queryClient.invalidateQueries(['query-bankruptcy', { id: n.bk_id }]);
          queryClient.invalidateQueries(['query-docket', n.bk_id]);

          const cache = queryClient.getQueryCache();
          cache
            .findAll('query-losses')
            .filter(
              (q) =>
                Array.isArray(q.queryKey) &&
                q.queryKey.length > 1 &&
                q.queryKey[1].filters.id === n.bk_id
            )
            .forEach((q) => queryClient.invalidateQueries(q.queryKey));
        });
      }

      return hasUnreadNotifications;
    },
    {
      // NOTE: refetch 10 seconds
      refetchInterval: 10000,
    }
  );
};

export const useGetNotifications = ({
  type,
  status,
  limit,
}: {
  type: NotificationType | 'all';
  status: NotificationStatus | 'all';
  limit?: number;
}) => {
  const { get } = useApi();

  return useQuery<NotificationRecord[], Error>(
    ['query-notifications', type, status, limit],
    async () => {
      const { data } = await get<NotificationRecord[]>('list-notifications', {
        params: {
          type,
          status,
          limit,
        },
      });
      return data;
    },
    {
      // NOTE: refetch 10 seconds
      refetchInterval: 10000,
    }
  );
};

export const useReadNotification = () => {
  const { post } = useApi();
  const queryClient = useQueryClient();

  const updateQueryData = useUpdateQueryData({
    queryKey: 'query-notifications',
    updater: (
      prevData: NotificationRecord[] | undefined,
      params: { id: number; read: boolean }
    ) =>
      (prevData || []).map((n) =>
        n.id === params.id
          ? ({
              ...n,
              status: 'read',
            } as NotificationRecord)
          : n
      ),
  });

  const updateUnreadQueryData = useUpdateQueryData({
    queryKey: 'query-unread-notifications',
    updater: (prevData: number, params: { read: boolean }) =>
      prevData + 1 * (params.read ? -1 : 1),
  });

  return useMutation(
    async (id: number) => {
      await post('/read-notification', { id });
      return true;
    },
    {
      onMutate: async (id) => {
        await queryClient.cancelQueries('query-notifications');

        updateQueryData({ id, read: true });
        updateUnreadQueryData({ read: true });
      },
      onError: (_, id) => {
        updateQueryData({ id, read: false });
        updateUnreadQueryData({ read: false });
      },
      onSettled: () => {
        queryClient.invalidateQueries(['query-notifications']);
        queryClient.invalidateQueries(['query-unread-notifications']);
      },
    }
  );
};

export const useReadNotifications = () => {
  const { post } = useApi();
  const queryClient = useQueryClient();

  return useMutation(
    async ({
      type,
      status,
      limit,
    }: {
      type: NotificationType | 'all';
      status: NotificationStatus | 'all';
      limit?: number;
    }) => {
      await post('/read-notifications', { type, status, limit });
      return true;
    },
    {
      onMutate: async (filters) => {
        await queryClient.cancelQueries('query-notifications');

        const prevNotifications = queryClient.getQueryData<
          NotificationRecord[]
        >(['query-notifications', filters.type, filters.status, filters.limit]);

        queryClient.setQueryData(
          ['query-notifications', filters.type, filters.status, filters.limit],
          (notifications: NotificationRecord[] | undefined) =>
            (notifications || []).map(
              (n) =>
                ({
                  ...n,
                  status: 'read',
                } as NotificationRecord)
            )
        );

        queryClient.setQueryData(['query-unread-notifications'], () => 0);

        return prevNotifications;
      },
      onError: (_, filters, prevNotifications?: NotificationRecord[]) => {
        queryClient.setQueryData(
          ['query-notifications', filters.type, filters.status, filters.limit],
          prevNotifications
        );

        queryClient.setQueryData(
          ['query-unread-notifications'],
          () => prevNotifications?.length ?? 0
        );
      },
      onSettled: () => {
        queryClient.invalidateQueries(['query-notifications']);
        queryClient.invalidateQueries(['query-unread-notifications']);
      },
    }
  );
};

export const useClearNotifications = () => {
  const { post } = useApi();
  const queryClient = useQueryClient();

  return useMutation(
    async ({
      type,
      status,
      limit,
    }: {
      type: NotificationType | 'all';
      status: NotificationStatus | 'all';
      limit?: number;
    }) => {
      await post('/delete-notifications', { type, status, limit });
      return true;
    },
    {
      onMutate: async (filters) => {
        await queryClient.cancelQueries('query-notifications');

        const prevNotifications = queryClient.getQueryData<
          NotificationRecord[]
        >(['query-notifications', filters.type, filters.status, filters.limit]);

        queryClient.setQueryData(
          ['query-notifications', filters.type, filters.status, filters.limit],
          () => []
        );

        return prevNotifications;
      },
      onError: (_, filters, prevNotifications) => {
        queryClient.setQueryData(
          ['query-notifications', filters.type, filters.status, filters.limit],
          prevNotifications
        );
      },
      onSettled: () => {
        queryClient.invalidateQueries(['query-notifications']);
        queryClient.invalidateQueries(['query-unread-notifications']);
      },
    }
  );
};

export const useGetSplash = () => {
  const { getNoAuth } = useApi();

  return useQuery<SplashItem[], Error>('query-splash', async () => {
    const { data } = await getNoAuth<SplashItem[]>('/splash-losses');

    return data;
  });
};
