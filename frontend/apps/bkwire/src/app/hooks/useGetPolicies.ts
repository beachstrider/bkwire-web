import axios from 'axios';
import { useEffect, useState } from 'react';

const policyKeys = {
  privacy: 'YlZneVJVbzRVVk5RVEhBdlNFRTlQUT09',
  cookies: 'TW5Ob2NtUkNZbk5xT0hOMFNsRTlQUT09',
  tos: 'ZW14WE0wWkthaTlDYlVwSlZHYzlQUT09',
  eula: 'VWxsSk5GY3dSSGxaWjJkdFJIYzlQUT09',
  disclaimer: 'TW5SNlJsSXliV2RDYVVKTVltYzlQUT09',
} as const;

export const policyTypes = Object.keys(policyKeys);

export type PolicyTypes = keyof typeof policyKeys;

export const useGetPolicies = () => {
  const [policies, setPolicies] = useState<Record<
    PolicyTypes,
    string
  > | null>();

  useEffect(() => {
    Promise.all(
      policyTypes.map((k) =>
        axios.get(
          `https://app.termageddon.com/api/policy/${
            policyKeys[k as PolicyTypes]
          }?table-style=accordion`
        )
      )
    )
      .then((ps) => {
        setPolicies(
          policyTypes.reduce((prev, key, i) => {
            prev[key as PolicyTypes] = ps[i].data;
            return prev;
          }, {} as Record<PolicyTypes, string>)
        );
      })
      .catch((e) => setPolicies(null));
  }, []);

  return policies;
};
