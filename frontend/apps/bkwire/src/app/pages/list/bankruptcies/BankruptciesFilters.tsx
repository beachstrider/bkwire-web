import React, { SyntheticEvent, useMemo, useState } from 'react';
import {
  AccordionDetails,
  AccordionSummary,
  Autocomplete,
  Box,
  Checkbox,
  ListItem,
  ListItemButton,
  ListItemIcon,
  Slider,
  TextField,
  TextFieldProps,
  Typography,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { FilterList, FilterListItem } from '../filters/Filters';
import { BankruptcyFilters } from '../../../api/api.types';
import {
  FilterAccordion,
  FiltersHeader,
  FiltersRoot,
} from '../filters/Filters.styled';
import { ButtonLink } from '../../../components/ButtonLink';
import { useGetCities } from '../../../api/api.hooks';
import { ranges, chapterTypes, states } from '../../../api/api.constants';
import { formatKMB } from '../../../utils/number';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { FilterListRoot } from '../filters/Filters.styled';

export const defaultBkFilters: BankruptcyFilters = {
  search: '',
  chapterTypes: [],
  dateAdded: [null, null],
  dateFiled: [null, null],
  state: '',
  city: '',
  assetRanges: [],
  liabilityRanges: [],
  involuntary: false,
  sub_chapv: false,
};

interface BankruptciesFiltersProps {
  filters: BankruptcyFilters;
  setFilters: React.Dispatch<React.SetStateAction<BankruptcyFilters>>;
}
export const BankruptciesFilters: React.FC<BankruptciesFiltersProps> = ({
  filters,
  setFilters,
}) => {
  const { data: cityInfos } = useGetCities(filters.state);

  const cities = [{ city: '' }, ...(cityInfos || [])].map((c) => c.city);

  const cTypeListItems: FilterListItem[] = useMemo(() => {
    return (
      chapterTypes.map((i) => ({
        id: i.id,
        name: i.name,
      })) || []
    );
  }, []);

  const onListFilterChange =
    (filter: keyof BankruptcyFilters) => (id: number) => () =>
      setFilters((prevFilters) => {
        const prevChecked = prevFilters[filter] as number[];
        const index = prevChecked.indexOf(id);
        const newChecked = [...prevChecked];

        if (index === -1) {
          newChecked.push(id);
        } else {
          newChecked.splice(index, 1);
        }

        return {
          ...prevFilters,
          [filter]: newChecked,
        };
      });

  const onInvoluntaryChanged = () =>
    setFilters((prevFilters) => ({
      ...prevFilters,
      involuntary: !prevFilters.involuntary,
    }));

  const onSubvChanged = () =>
    setFilters((prevFilters) => ({
      ...prevFilters,
      sub_chapv: !prevFilters.sub_chapv,
    }));

  const onStartDateAddedChanged = (value: Date | null) =>
    setFilters((prevFilters) => ({
      ...prevFilters,
      dateAdded: [value, prevFilters.dateAdded[1]],
    }));

  const onEndDateAddedChanged = (value: Date | null) =>
    setFilters((prevFilters) => ({
      ...prevFilters,
      dateAdded: [prevFilters.dateAdded[0], value],
    }));

  const onStartDateFiledChanged = (value: Date | null) =>
    setFilters((prevFilters) => ({
      ...prevFilters,
      dateFiled: [value, prevFilters.dateFiled[1]],
    }));

  const onEndDateFiledChanged = (value: Date | null) =>
    setFilters((prevFilters) => ({
      ...prevFilters,
      dateFiled: [prevFilters.dateFiled[0], value],
    }));

  const onStateChanged = (value: string | null) =>
    setFilters((prevFilters) => ({
      ...prevFilters,
      state: value || '',
      city: '',
    }));

  const onCityChanged = (value: string | null) =>
    setFilters((prevFilters) => ({
      ...prevFilters,
      city: value || '',
    }));

  const [assetRangeIndex, setAssetRangeIndex] = useState<number[]>(
    filters.assetRanges.length
      ? [
          filters.assetRanges[0] - 1,
          filters.assetRanges[filters.assetRanges.length - 1] - 1,
        ]
      : [0, ranges.length - 1]
  );

  const [liabilityRangeIndex, setLiabilityRangeIndex] = useState<number[]>(
    filters.liabilityRanges.length
      ? [
          filters.liabilityRanges[0] - 1,
          filters.liabilityRanges[filters.liabilityRanges.length - 1] - 1,
        ]
      : [0, ranges.length - 1]
  );

  const onRangeChange =
    (rangeProp: 'assetRanges' | 'liabilityRanges') =>
    (
      _: Event | SyntheticEvent<Element, Event>,
      indexRange: number | number[]
    ) => {
      const rangeFilters = [];
      for (
        let i = (indexRange as number[])[0];
        i <= (indexRange as number[])[1];
        i++
      ) {
        rangeFilters.push(i + 1);
      }
      setFilters({
        ...filters,
        [rangeProp]: rangeFilters,
      });
    };

  const clearFilters = () => {
    setFilters(defaultBkFilters);
    setAssetRangeIndex([0, ranges.length - 1]);
    setLiabilityRangeIndex([0, ranges.length - 1]);
  };

  return (
    <FiltersRoot>
      <FiltersHeader>
        <Typography variant="body2">Filter</Typography>
        <ButtonLink onClick={clearFilters}>Clear all</ButtonLink>
      </FiltersHeader>
      <FilterAccordion square disableGutters defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="body2">Chapter type</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <FilterList
            idPrefix="filter-chapter-types"
            items={cTypeListItems}
            value={filters.chapterTypes}
            onChange={onListFilterChange('chapterTypes')}
          >
            <ListItem>
              <ListItemButton dense onClick={() => onInvoluntaryChanged()}>
                <ListItemIcon>
                  <Checkbox size="small" checked={filters.involuntary} />
                </ListItemIcon>
                <Typography variant="body2">Involuntary</Typography>
              </ListItemButton>
            </ListItem>
            <ListItem>
              <ListItemButton dense onClick={() => onSubvChanged()}>
                <ListItemIcon>
                  <Checkbox size="small" checked={filters.sub_chapv} />
                </ListItemIcon>
                <Typography variant="body2">Sub Chapter V</Typography>
              </ListItemButton>
            </ListItem>
          </FilterList>
        </AccordionDetails>
      </FilterAccordion>
      <FilterAccordion square disableGutters defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="body2">Date added</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box display="flex" flexDirection="column" py={1} px={2} mb={1}>
            <Typography variant="body3">Start date</Typography>
            <DatePicker
              label=""
              value={filters.dateAdded[0]}
              onChange={onStartDateAddedChanged}
              OpenPickerButtonProps={{
                sx: { mr: '-10px', svg: { fontSize: '1rem' } },
              }}
              renderInput={(params: TextFieldProps) => (
                <TextField
                  label=""
                  size="small"
                  variant="standard"
                  sx={{ input: { fontSize: 14 } }}
                  {...params}
                />
              )}
            />
          </Box>
          <Box display="flex" flexDirection="column" py={1} px={2} mb={2}>
            <Typography variant="body3">End date</Typography>
            <DatePicker
              label=""
              value={filters.dateAdded[1]}
              onChange={onEndDateAddedChanged}
              OpenPickerButtonProps={{
                sx: { mr: '-10px', svg: { fontSize: '1rem' } },
              }}
              renderInput={(params: TextFieldProps) => (
                <TextField
                  label=""
                  size="small"
                  variant="standard"
                  sx={{ input: { fontSize: 14 } }}
                  {...params}
                />
              )}
            />
          </Box>
        </AccordionDetails>
      </FilterAccordion>
      <FilterAccordion square disableGutters>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="body2">Date filed</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box display="flex" flexDirection="column" py={1} px={2} mb={1}>
            <Typography variant="body3">Start date</Typography>
            <DatePicker
              label=""
              value={filters.dateFiled[0]}
              onChange={onStartDateFiledChanged}
              OpenPickerButtonProps={{
                sx: { mr: '-10px', svg: { fontSize: '1rem' } },
              }}
              renderInput={(params: TextFieldProps) => (
                <TextField
                  label=""
                  size="small"
                  variant="standard"
                  sx={{ input: { fontSize: 14 } }}
                  {...params}
                />
              )}
            />
          </Box>
          <Box display="flex" flexDirection="column" py={1} px={2} mb={2}>
            <Typography variant="body3">End date</Typography>
            <DatePicker
              label=""
              value={filters.dateFiled[1]}
              onChange={onEndDateFiledChanged}
              OpenPickerButtonProps={{
                sx: { mr: '-10px', svg: { fontSize: '1rem' } },
              }}
              renderInput={(params: TextFieldProps) => (
                <TextField
                  label=""
                  size="small"
                  variant="standard"
                  sx={{ input: { fontSize: 14 } }}
                  {...params}
                />
              )}
            />
          </Box>
        </AccordionDetails>
      </FilterAccordion>
      <FilterAccordion square disableGutters defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="body2">Asset range ($)</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box py={1} px={2}>
            <Typography variant="body3">
              {formatKMB(ranges[assetRangeIndex[0]].min)}
              {' to '}
              {formatKMB(ranges[assetRangeIndex[1]].max)}
            </Typography>
            <Slider
              size="small"
              valueLabelDisplay="off"
              disableSwap
              min={0}
              max={ranges.length - 1}
              step={1}
              value={assetRangeIndex}
              onChange={(_, v) => setAssetRangeIndex(v as number[])}
              onChangeCommitted={onRangeChange('assetRanges')}
            />
          </Box>
        </AccordionDetails>
      </FilterAccordion>
      <FilterAccordion square disableGutters defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="body2">Liability range ($)</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box py={1} px={2}>
            <Typography variant="body3">
              {formatKMB(ranges[liabilityRangeIndex[0]].min)}
              {' to '}
              {formatKMB(ranges[liabilityRangeIndex[1]].max)}
            </Typography>
            <Slider
              size="small"
              valueLabelDisplay="off"
              disableSwap
              min={0}
              max={ranges.length - 1}
              step={1}
              value={liabilityRangeIndex}
              onChange={(_, v) => setLiabilityRangeIndex(v as number[])}
              onChangeCommitted={onRangeChange('liabilityRanges')}
            />
          </Box>
        </AccordionDetails>
      </FilterAccordion>
      <FilterAccordion square disableGutters>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="body2">Location</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box py={1} px={2} mb={2}>
            <Autocomplete
              disablePortal
              autoHighlight
              fullWidth
              sx={{
                '.MuiAutocomplete-endAdornment': {
                  transform: 'translateX(5px)',
                },
              }}
              value={filters.state}
              onChange={(_: unknown, newValue: string | null) => {
                onStateChanged(newValue);
              }}
              options={Object.keys(states)}
              getOptionLabel={(o) => states[o]}
              renderInput={(params) => (
                <TextField
                  {...params}
                  sx={{
                    input: {
                      fontSize: 14,
                    },
                    mb: 2,
                  }}
                  fullWidth
                  variant="standard"
                  margin="none"
                  label="State"
                />
              )}
            />
            <Autocomplete
              disablePortal
              autoHighlight
              fullWidth
              sx={{
                '.MuiAutocomplete-endAdornment': {
                  transform: 'translateX(5px)',
                },
              }}
              value={filters.city}
              onChange={(_: unknown, newValue: string | null) => {
                onCityChanged(newValue);
              }}
              disabled={!filters.state}
              options={cities}
              getOptionLabel={(o) => o || 'Any city'}
              renderInput={(params) => (
                <TextField
                  {...params}
                  sx={{
                    input: {
                      fontSize: 14,
                    },
                    mb: 2,
                  }}
                  fullWidth
                  variant="standard"
                  margin="none"
                  label="City"
                />
              )}
            />
          </Box>
        </AccordionDetails>
      </FilterAccordion>
    </FiltersRoot>
  );
};
