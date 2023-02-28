import React, { useState } from 'react';
import { LossesGrid } from '../list/losses/LossesGrid';
import { LossFilters } from '../../api/api.types';
import { defaultLossFilters } from '../list/losses/LossesFilters';

export const CompaniesWatchlist: React.VFC = () => {
  const [filters] = useState<LossFilters>(defaultLossFilters);

  return (
    <LossesGrid filters={filters} industriesFilter={[]} mode="watchlist" />
  );
};
