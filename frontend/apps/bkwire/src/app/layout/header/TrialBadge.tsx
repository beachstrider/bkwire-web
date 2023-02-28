import React, { useMemo } from 'react';
import { TrialBadgeRoot } from './Header.styled';
import { useGetViewer } from '../../api/api.hooks';
import { differenceInDays } from 'date-fns';
import { ButtonLink } from '../../components/ButtonLink';
import { TRIAL_DAYS } from '../../api/api.constants';

export const TrialBadge = () => {
  const { data: viewer } = useGetViewer();
  const days = useMemo(() => {
    const ellapsed = viewer
      ? differenceInDays(new Date(), new Date(viewer.date_added))
      : TRIAL_DAYS;
    return Math.max(0, TRIAL_DAYS - ellapsed);
  }, [viewer]);

  return (
    <TrialBadgeRoot
      display={
        viewer?.subscription === 'none' || viewer?.subscription === 'trial'
          ? 'block'
          : 'none'
      }
    >
      <ButtonLink
        variant="contained"
        color="error"
        size="small"
        fontWeight={500}
        to="/account/billing"
      >
        {days > 0
          ? `Trial ${days} day${days !== 1 ? 's' : ''} remaining`
          : 'Trial ended'}
      </ButtonLink>
    </TrialBadgeRoot>
  );
};
