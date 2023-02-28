import { Box } from '@mui/system';
import { Typography } from '@mui/material';
import { Loading } from '../loading/Loading';
import { addDays, isLastDayOfMonth } from 'date-fns';
import { HistogramRoot, HistogramColumn } from './Histogram.styled';

export interface HistogramProps {
  xLabel: string;
  yLabel: string;
  legend: string;
  loading: boolean;
  columns: number[];
  lastDate?: Date;
}
export const Histogram = ({
  xLabel,
  yLabel,
  legend,
  loading,
  columns,
  lastDate,
}: HistogramProps) => {
  if (loading) {
    return <Loading />;
  }

  const yAxis = {
    10: [0, 2, 4, 6, 8, 10],
    20: [0, 5, 10, 15, 20],
    30: [0, 6, 12, 18, 24, 30],
    40: [0, 10, 20, 30, 40],
    50: [0, 10, 20, 30, 40, 50],
    60: [0, 15, 30, 45, 60],
    80: [0, 20, 40, 60, 80],
    100: [0, 25, 50, 75, 100],
    200: [0, 50, 100, 150, 200],
    300: [0, 75, 150, 225, 300],
    400: [0, 100, 200, 300, 400],
    500: [0, 125, 250, 375, 500],
    600: [0, 150, 300, 450, 600],
    800: [0, 200, 400, 600, 800],
    1000: [0, 250, 500, 750, 1000],
  };

  const maxCol = Math.max(...columns);
  const ySteps = (
    Object.entries(yAxis).find((e) => Number(e[0]) >= maxCol)?.[1] || yAxis[100]
  ).reverse();

  const renderColumn = (day: number, index: number) => {
    let date = lastDate || new Date();
    date = addDays(date, -(columns.length - 1 - index));

    const dayOfMonth = date.getDate();
    const isFirstDay = dayOfMonth === 1;
    const showDay =
      isFirstDay ||
      (index % 5 === 0 && dayOfMonth !== 2 && !isLastDayOfMonth(date));

    const formattedDay = date.toLocaleDateString('en-US', {
      month: 'short',
      day: date.getDate() === 1 ? undefined : 'numeric',
    });

    return (
      <HistogramColumn key={formattedDay} emphasize={isFirstDay}>
        <Box className="h-column" height={`${(day / ySteps[0]) * 100}%`}>
          <Typography className="h-count" variant="body2">
            {day}
          </Typography>
          {showDay && (
            <Typography className="h-date" variant="body3">
              {formattedDay}
            </Typography>
          )}
        </Box>
      </HistogramColumn>
    );
  };

  return (
    <HistogramRoot yStepCount={ySteps.length}>
      <Box className="top">
        <Box className="y-label">
          <Typography variant="verticalLabel">{xLabel}</Typography>
        </Box>
        <Box className="y-steps">
          {ySteps.map((y) => (
            <Typography variant="body3" key={y}>
              {y}
            </Typography>
          ))}
        </Box>
        <Box className="histogram">{columns.map(renderColumn)}</Box>
      </Box>

      <Box className="bottom">
        <Box className="x-label">
          <Typography variant="horizontalLabel">{yLabel}</Typography>
        </Box>
      </Box>
      <Typography variant="body3" className="legend">
        {legend}
      </Typography>
    </HistogramRoot>
  );
};
