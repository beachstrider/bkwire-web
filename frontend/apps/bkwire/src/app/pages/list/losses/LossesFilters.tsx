import React, { SyntheticEvent, useState } from 'react';
import {
  AccordionDetails,
  AccordionSummary,
  Autocomplete,
  Box,
  Slider,
  TextField,
  TextFieldProps,
  Typography,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { LossFilters } from '../../../api/api.types';
import {
  FilterAccordion,
  FiltersHeader,
  FiltersRoot,
} from '../filters/Filters.styled';
import { ButtonLink } from '../../../components/ButtonLink';
import { useGetCities } from '../../../api/api.hooks';
import { states } from '../../../api/api.constants';
import { formatKMB, formatRangeKMB } from '../../../utils/number';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';

const lossValues = [
  0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 20000, 30000,
  40000, 50000, 60000, 70000, 80000, 90000, 100000, 200000, 300000, 400000,
  500000, 600000, 700000, 800000, 900000, 1000000, 2000000, 3000000, 4000000,
  5000000, 6000000, 7000000, 8000000, 9000000, 10000000, 20000000, 30000000,
  40000000, 50000000, 60000000, 70000000, 80000000, 90000000, 100000000,
  1000000000, 10000000000, 100000000000,
];
const lossMarks = [0, 10000, 100000, 1000000, 10000000, 100000000].map((v) => ({
  value: lossValues.indexOf(v),
  label: formatKMB(v),
}));

export const defaultLossFilters: LossFilters = {
  search: '',
  loss: [lossValues[0], lossValues[lossValues.length - 1]],
  dateAdded: [null, null],
  dateFiled: [null, null],
  state: '',
  city: '',
  max_losses_per_case: null,
  id: null,
};

interface LossesFiltersProps {
  filters: LossFilters;
  setFilters: React.Dispatch<React.SetStateAction<LossFilters>>;
}
export const LossesFilters: React.FC<LossesFiltersProps> = ({
  filters,
  setFilters,
}) => {
  const { data: cityInfos } = useGetCities(filters.state);

  const cities = [{ city: '' }, ...(cityInfos || [])].map((c) => c.city);

  const [lossIndex, setLossIndex] = useState<number[]>(
    filters.loss.length === 2
      ? [
          lossValues.indexOf(filters.loss[0]),
          lossValues.indexOf(filters.loss[1]),
        ]
      : [0, lossValues.length - 1]
  );

  const onLossChange = (
    _: Event | SyntheticEvent<Element, Event>,
    lossIndexRange: number | number[]
  ) =>
    setFilters({
      ...filters,
      loss: [
        lossValues[(lossIndexRange as number[])[0]],
        lossValues[(lossIndexRange as number[])[1]],
      ],
    });

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

  const clearFilters = () => {
    setFilters(defaultLossFilters);
    setLossIndex([0, lossValues.length - 1]);
  };

  return (
    <FiltersRoot>
      <FiltersHeader>
        <Typography variant="body2">Filter</Typography>
        <ButtonLink onClick={clearFilters}>Clear all</ButtonLink>
      </FiltersHeader>
      <FilterAccordion square disableGutters defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="body2">Loss amount</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box py={1} px={2}>
            <Typography variant="body3">
              {formatRangeKMB({
                min: lossValues[lossIndex[0]],
                max: lossValues[lossIndex[1]],
              })}{' '}
              ($)
            </Typography>
            <Slider
              size="small"
              valueLabelDisplay="off"
              disableSwap
              min={0}
              max={lossValues.length - 1}
              step={1}
              marks={lossMarks}
              value={lossIndex}
              onChange={(_, v) => setLossIndex(v as number[])}
              onChangeCommitted={onLossChange}
            />
          </Box>
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
