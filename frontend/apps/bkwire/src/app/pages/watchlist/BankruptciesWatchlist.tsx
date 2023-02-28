import React, { useState } from 'react';
import { BankruptcyFilters } from '../../api/api.types';
import { defaultBkFilters } from '../list/bankruptcies/BankruptciesFilters';
import { BankruptciesGrid } from '../list/bankruptcies/BankruptciesGrid';

export const BankruptciesWatchlist: React.VFC = () => {
  const [filters] = useState<BankruptcyFilters>(defaultBkFilters);

  return (
    <BankruptciesGrid
      filters={filters}
      industriesFilter={[]}
      mode="watchlist"
    />
  );
};
