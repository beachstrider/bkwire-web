import { useCallback, useMemo } from 'react';
import {
  GridRenderCellParams,
  GridValueFormatterParams,
} from '@mui/x-data-grid';
import { ButtonLink } from '../components/ButtonLink';
import { Box, Typography } from '@mui/material';
import { formatAmount, formatRange, formatRangeKMB } from '../utils/number';
import { formatDateRelative, toDateSafe } from '../utils/date';
import dateFormat from 'date-fns/format';

export const useFormatters = () => {
  const naValue = 'see petition';

  const industryFormatter = useCallback(
    (params: GridRenderCellParams) =>
      params.value || <Typography variant="caption">{naValue}</Typography>,
    []
  );

  const industryValueFormatter = useCallback(
    (params: GridValueFormatterParams) => params.value || naValue,
    []
  );

  const ctFormatter = useCallback(
    (params: GridRenderCellParams) => params.value,
    // `${params.value} ${
    //   params.value === 7 ? 'Liquidation' : 'Reorganization'
    // }`,
    []
  );

  const ctValueFormatter = useCallback(
    (params: GridValueFormatterParams) => params.value,
    // `${params.value} ${
    //   params.value === 7 ? 'Liquidation' : 'Reorganization'
    // }`,
    []
  );

  const naFormatter = useCallback(
    (params: GridRenderCellParams) =>
      params.value || <Typography variant="caption">{naValue}</Typography>,
    []
  );

  const naValueFormatter = useCallback(
    (params: GridValueFormatterParams) => params.value || naValue,
    []
  );

  const dateFormatter = useCallback((params: GridRenderCellParams) => {
    return dateFormat(toDateSafe(params.value), 'MM-dd-yy');
  }, []);

  const relativeDateFormatter = useCallback(
    (params: GridRenderCellParams) =>
      params.value ? (
        formatDateRelative(toDateSafe(params.value), '', 'ago')
      ) : (
        <Typography variant="caption">{naValue}</Typography>
      ),
    []
  );

  const amountFormatter = useCallback(
    (params: GridRenderCellParams) =>
      params.value ? (
        formatAmount(params.value)
      ) : (
        <Typography variant="caption">{naValue}</Typography>
      ),
    []
  );

  const amountValueFormatter = useCallback(
    (params: GridValueFormatterParams) =>
      params.value ? formatAmount(Number(params.value)) : naValue,
    []
  );

  const linkFormatter = useCallback(
    (to: string, idPropName: string) => (params: GridRenderCellParams) =>
      params.value ? (
        <ButtonLink to={`${to}/${params.row[idPropName]}`}>
          {params.value}
        </ButtonLink>
      ) : (
        <Typography variant="caption">{naValue}</Typography>
      ),
    []
  );

  const rangeFormatter = useCallback(
    (minCellField: string, naOverride?: string) =>
      ({ id, value: max, row }: GridRenderCellParams) => {
        const min = id ? row[minCellField] : null;
        return min === null && max === null ? (
          <Typography variant="caption">{naValue}</Typography>
        ) : min === -1 || max === -1 ? (
          <Typography variant="caption">{naOverride}</Typography>
        ) : (
          formatRange({
            min: Number(min),
            max: Number(max),
          })
        );
      },
    []
  );

  const rangeValueFormatter = useCallback(
    (minCellField: string, naValueOverride?: string) =>
      ({ id, value: max, api }: GridValueFormatterParams) => {
        const min = id ? api.getRow(id)[minCellField] : null;
        return min === null && max === null
          ? naValue
          : min === -1 || max === -1
          ? naValueOverride
          : ' ' + // this is a hack to prevent excel from showing this as a date
            formatRange({
              min: Number(min),
              max: Number(max),
            });
      },
    []
  );

  const rangeFormatterKMB = useCallback(
    (minCellField: string, naOverride?: string) =>
      ({ id, value: max, row }: GridRenderCellParams) => {
        const min = id ? row[minCellField] : null;
        return min === null && max === null ? (
          <Typography variant="caption">{naValue}</Typography>
        ) : min === -1 || max === -1 ? (
          <Typography variant="caption">{naOverride}</Typography>
        ) : (
          formatRangeKMB({
            min: Number(min),
            max: Number(max),
          })
        );
      },
    []
  );

  const rangeValueFormatterKMB = useCallback(
    (minCellField: string, naValueOverride?: string) =>
      ({ id, value: max, api }: GridValueFormatterParams) => {
        const min = id ? api.getRow(id)[minCellField] : null;
        return min === null && max === null
          ? naValue
          : min === -1 || max === -1
          ? naValueOverride
          : formatRangeKMB({
              min: Number(min),
              max: Number(max),
            });
      },
    []
  );

  const activityFormatter = useCallback(
    (params: GridRenderCellParams) =>
      params.value ? (
        <Typography variant="body2">
          <span dangerouslySetInnerHTML={{ __html: params.value }} />
        </Typography>
      ) : (
        <Typography variant="caption">{naValue}</Typography>
      ),
    []
  );

  const docsPagesFormatter = useCallback(
    (docsField: string) =>
      ({ id, value: pages, row }: GridRenderCellParams) => {
        const docs = id ? row[docsField] : null;
        return docs + pages > 0 ? (
          <Box>
            <Typography variant="body2">{pages || 0} pages</Typography>
            <Typography variant="body3">{docs || 0} docs</Typography>
          </Box>
        ) : (
          <> </>
        );
      },
    []
  );

  return {
    industryFormatter,
    industryValueFormatter,
    ctFormatter,
    ctValueFormatter,
    naFormatter,
    naValueFormatter,
    dateFormatter,
    relativeDateFormatter,
    amountFormatter,
    amountValueFormatter,
    linkFormatter,
    rangeFormatter,
    rangeValueFormatter,
    rangeFormatterKMB,
    rangeValueFormatterKMB,
    activityFormatter,
    docsPagesFormatter,
  };
};
