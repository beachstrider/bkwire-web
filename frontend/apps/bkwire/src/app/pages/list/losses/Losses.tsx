import React, { useState, useEffect } from 'react';
import { PagePaper } from '../../../components/PagePaper.styled';
import { LossesGrid } from './LossesGrid';
import { LossesFilters, defaultLossFilters } from './LossesFilters';
import { LossFilters } from '../../../api/api.types';
import { useQueryStringState } from '../../../hooks/useQueryStringState';

export const Losses = ({
  industriesFilter,
}: {
  industriesFilter: number[];
}) => {
  const [q, setQ] = useQueryStringState<string>(
    'q',
    JSON.stringify(defaultLossFilters)
  );

  const [filters, setFilters] = useState<LossFilters>(JSON.parse(q));

  useEffect(() => {
    const newFilters = JSON.parse(q);
    if (filters !== newFilters) {
      setFilters(newFilters);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q]);

  useEffect(() => {
    const stringifiedFilters = JSON.stringify(filters);
    if (q !== stringifiedFilters) {
      setQ(stringifiedFilters);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  return (
    <>
      <LossesFilters filters={filters} setFilters={setFilters} />
      <PagePaper flexGrow={1}>
        <LossesGrid
          filters={filters}
          setFilters={setFilters}
          industriesFilter={industriesFilter}
        />
      </PagePaper>
    </>
  );
};
