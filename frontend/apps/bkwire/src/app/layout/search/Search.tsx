import React, { useState, useRef } from 'react';
import TextField from '@mui/material/TextField';
import Autocomplete, {
  AutocompleteRenderGroupParams,
} from '@mui/material/Autocomplete';
import CircularProgress from '@mui/material/CircularProgress';
import { Box, Button, InputAdornment } from '@mui/material';
import { Clear, SearchOutlined } from '@mui/icons-material';
import { SearchGroup, SearchOption, SearchRoot } from './Search.styled';
import { useNavigate } from 'react-router';
import { useSearch } from '../../api/api.hooks';
import { useDebounce } from '../../hooks/useDebounce';
import { formatKMB } from '../../utils/number';
import { defaultBkFilters } from '../../pages/list/bankruptcies/BankruptciesFilters';
import { defaultLossFilters } from '../../pages/list/losses/LossesFilters';

interface OptionData {
  id: number;
  type: string;
  title: string;
  amount: string;
}

const BoldMatchText: React.FC<{ text: string; match: string }> = ({
  text,
  match,
}) => (
  <Box
    dangerouslySetInnerHTML={{
      __html: text.replace(
        new RegExp(`${match.replace(/[-[\]/{}()*+?.\\^$|]/g, '\\$&')}`, 'i'),
        '<b>$&</b>'
      ),
    }}
  />
);

export const Search: React.VFC = () => {
  const [open, setOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [value, setValue] = useState<OptionData | null>(null);

  const debouncedSearch = useDebounce(inputValue, 400);
  const { isLoading, data } = useSearch(debouncedSearch, 5);

  const options: OptionData[] = [
    ...(data?.bankruptcies.map((b) => ({
      id: b.dci_id,
      type: 'Bankruptcies',
      title: b.case_name,
      amount: b.total_loss ? `$${formatKMB(b.total_loss)}` : '',
    })) || []),
    ...(data?.losses.map((l) => ({
      id: l.dci_id,
      type: 'Corporate losses',
      title: l.creditor_name,
      amount: l.unsecured_claim ? `$${formatKMB(l.unsecured_claim)}` : '',
    })) || []),
  ];

  const navigate = useNavigate();

  const inputRef = useRef<HTMLDivElement | null>(null);

  const blur = () => {
    setInputValue('');
    setValue(null);
  };

  return (
    <SearchRoot showResults={Boolean(inputValue) && !isLoading} mr={2}>
      <Autocomplete
        open={open}
        onOpen={() => setOpen(true)}
        onClose={() => setOpen(false)}
        value={value}
        onChange={(_, newValue: OptionData | null) => {
          if (newValue) {
            navigate(`/view/bankruptcy/${newValue.id}`);
            setValue(null);
          }
        }}
        onInputChange={(_, newInputValue) => setInputValue(newInputValue)}
        isOptionEqualToValue={(o, v) => o.title === v.title}
        getOptionLabel={(o) => o.title}
        options={options}
        groupBy={(o) => o.type}
        clearIcon={!isLoading ? <Clear fontSize="small" /> : null}
        loading={isLoading}
        forcePopupIcon={false}
        noOptionsText="0 results"
        blurOnSelect
        fullWidth
        disablePortal
        renderGroup={(params: AutocompleteRenderGroupParams) => (
          <SearchGroup key={params.key}>
            <Box className="search-group-header">
              <Box>
                {params.group === 'Bankruptcies'
                  ? 'Corporate Bankruptcies'
                  : 'Impacted Businesses'}
              </Box>
              <Button
                variant="link"
                onClick={() => {
                  blur();
                  const searchParams = new URLSearchParams();
                  searchParams.set(
                    'q',
                    JSON.stringify({
                      ...(params.group === 'Bankruptcies'
                        ? defaultBkFilters
                        : defaultLossFilters),
                      search: debouncedSearch,
                    })
                  );
                  navigate({
                    pathname:
                      params.group === 'Bankruptcies'
                        ? '/list/bankruptcies'
                        : '/list/losses',
                    search: searchParams.toString(),
                  });
                }}
              >
                View all
              </Button>
            </Box>
            <Box className="search-group-options">{params.children}</Box>
          </SearchGroup>
        )}
        renderOption={(props: unknown, option: OptionData) => (
          <SearchOption {...props} key={option.id}>
            <BoldMatchText text={option.title} match={inputValue} />
            <Box>{option.amount}</Box>
          </SearchOption>
        )}
        renderInput={(params) => (
          <TextField
            ref={inputRef}
            {...params}
            value={inputValue}
            InputProps={{
              ...params.InputProps,
              placeholder: open
                ? 'Start typing a company name (E.g. express)'
                : 'Power search',
              startAdornment: (
                <InputAdornment position="start">
                  <SearchOutlined />
                </InputAdornment>
              ),
              endAdornment: (
                <>
                  {isLoading ? (
                    <CircularProgress color="inherit" size={20} />
                  ) : null}
                  {params.InputProps.endAdornment}
                </>
              ),
            }}
          />
        )}
      />
    </SearchRoot>
  );
};
