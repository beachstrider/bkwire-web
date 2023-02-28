import { useEffect, useState } from 'react';
import { PagePaper } from '../../../components/PagePaper.styled';
import { BankruptciesGrid } from './BankruptciesGrid';
import { BankruptciesFilters, defaultBkFilters } from './BankruptciesFilters';
import { BankruptcyFilters } from '../../../api/api.types';
import { useQueryStringState } from '../../../hooks/useQueryStringState';

export const Bankruptcies = ({
  industriesFilter,
}: {
  industriesFilter: number[];
}) => {
  const [q, setQ] = useQueryStringState<string>(
    'q',
    JSON.stringify(defaultBkFilters)
  );

  const [filters, setFilters] = useState<BankruptcyFilters>(JSON.parse(q));

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
      <BankruptciesFilters filters={filters} setFilters={setFilters} />
      <PagePaper flexGrow={1}>
        <BankruptciesGrid
          filters={filters}
          setFilters={setFilters}
          industriesFilter={industriesFilter}
        />
      </PagePaper>
    </>
  );
};
