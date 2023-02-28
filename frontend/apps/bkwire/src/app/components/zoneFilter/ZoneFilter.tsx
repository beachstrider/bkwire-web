import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Box, Button, Chip, DialogActions, IconButton } from '@mui/material';
import { useGetIndustries, useGetViewer } from '../../api/api.hooks';
import { Add } from '@mui/icons-material';
import { useQueryStringState } from '../../hooks/useQueryStringState';
import { allIndustries } from '../../api/api.constants';
import { ZoneFilterDialog, ZoneFilterRoot } from './ZoneFilter.styled';
import { SelectMatrix } from '../selectMatrix/SelectMatrix';

interface ZoneFilterProps {
  industriesFilter: number[];
  setIndustriesFilter: React.Dispatch<React.SetStateAction<number[]>>;
}

export const ZoneFilter = ({
  industriesFilter,
  setIndustriesFilter,
}: ZoneFilterProps) => {
  const { data: viewer, isLoading: viewerLoading } = useGetViewer();
  const { data: industries, isLoading: industriesLoading } = useGetIndustries();

  const [industriesQs, setIndustriesQs] = useQueryStringState<string[]>(
    'industries',
    allIndustries,
    'app',
    viewer?.email_address || ''
  );

  const viewerIndustries = useMemo(() => {
    return viewer?.industry_naics_code?.split(',') || allIndustries;
  }, [viewer?.industry_naics_code]);

  const isViewerIndustries = useMemo(() => {
    return industriesQs.join(',') === viewer?.industry_naics_code;
  }, [industriesQs, viewer?.industry_naics_code]);

  const isAllIndustries = useMemo(() => {
    return industriesQs.length === 1 && industriesQs[0] === 'all';
  }, [industriesQs]);

  //   const isLoading = viewerLoading || industriesLoading || !industriesQs.length;

  useEffect(() => {
    if (viewer) {
      const industriesQsArray = industriesQs
        .filter((i) => !isNaN(Number(i)))
        .map(Number);

      if (industriesFilter.join(',') !== industriesQsArray.join(',')) {
        setIndustriesFilter(industriesQsArray);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [viewer, industriesQs]);

  const [isFiltersModalOpen, setFiltersModalOpen] = useState(false);
  const [modalIndustryFilters, setModalIndustryFilters] = useState<number[]>(
    []
  );

  const openIndustryPicker = useCallback(() => {
    setModalIndustryFilters(
      industriesQs.filter((i) => !isNaN(Number(i))).map(Number)
    );
    setFiltersModalOpen(true);
  }, [industriesQs]);

  const handleFiltersModalClose = useCallback(
    () => setFiltersModalOpen(false),
    [setFiltersModalOpen]
  );

  const updateIndustryFilters = useCallback(() => {
    setFiltersModalOpen(false);

    const newIndustriesFilter =
      modalIndustryFilters.length === industries?.length ||
      modalIndustryFilters.length === 0
        ? allIndustries
        : modalIndustryFilters.map(String);

    if (industriesQs.join(',') !== newIndustriesFilter.join(',')) {
      setIndustriesQs(newIndustriesFilter);
    }
  }, [industriesQs, setIndustriesQs, industries?.length, modalIndustryFilters]);

  const deleteFilter = useCallback(
    (id: number) => () => {
      let newIndustriesFilter = industriesQs.filter((i) => Number(i) !== id);
      if (!newIndustriesFilter.length) {
        newIndustriesFilter = allIndustries;
      }
      if (industriesQs.join(',') !== newIndustriesFilter.join(',')) {
        setIndustriesQs(newIndustriesFilter);
      }
    },
    [industriesQs, setIndustriesQs]
  );

  const setFilterAll = useCallback(() => {
    if (industriesQs.join(',') !== allIndustries.join(',')) {
      setIndustriesQs(allIndustries);
    }
  }, [industriesQs, setIndustriesQs]);

  const setFilterWatched = useCallback(() => {
    if (industriesQs.join(',') !== viewerIndustries.join(',')) {
      setIndustriesQs(viewerIndustries);
    }
  }, [industriesQs, setIndustriesQs, viewerIndustries]);

  return (
    <>
      <ZoneFilterRoot>
        <Chip
          variant={isAllIndustries ? 'filled' : 'outlined'}
          label="All"
          color="primary"
          onClick={setFilterAll}
        />

        <Chip
          variant={isViewerIndustries ? 'filled' : 'outlined'}
          label="Watched"
          color="primary"
          onClick={setFilterWatched}
        />

        {industries &&
          industriesQs.map((id) => {
            const industry = industries.find((i) => i.value === Number(id));
            return (
              industry && (
                <Chip
                  key={industry.value}
                  label={industry.text}
                  onDelete={deleteFilter(industry.value)}
                />
              )
            );
          })}

        <IconButton size="small" onClick={openIndustryPicker}>
          <Add />
        </IconButton>
      </ZoneFilterRoot>

      <ZoneFilterDialog
        open={isFiltersModalOpen}
        onClose={handleFiltersModalClose}
      >
        <Box display="flex" flexDirection="column" p={2} pb={1} width={600}>
          <SelectMatrix
            options={industries}
            selected={modalIndustryFilters}
            setSelected={setModalIndustryFilters}
          />
        </Box>
        <DialogActions>
          <Button
            variant="outlined"
            color="primary"
            onClick={handleFiltersModalClose}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={updateIndustryFilters}
            autoFocus
          >
            Apply filters
          </Button>
        </DialogActions>
      </ZoneFilterDialog>
    </>
  );
};
