import React, { useCallback, useState } from 'react';
import { Box, Typography, useTheme } from '@mui/material';
import { useGetViewer } from '../../api/api.hooks';
import { Loading } from '../../components/loading/Loading';
import { CardMembership } from '@mui/icons-material';
import useApi from '../../api/api.client';
import { ButtonLink } from '../../components/ButtonLink';
import { PricingTable } from '../../components/PricingTable';

export const Billing: React.VFC = () => {
  const theme = useTheme();
  const { get } = useApi();
  const { data: viewer, isLoading: isViewerLoading } = useGetViewer();

  const [planName, setPlanName] = useState('');
  const [pending, setPending] = useState<string | null>(null);

  const onManage = useCallback(
    async (handler) => {
      if (viewer) {
        setPending(handler);
        try {
          const res = await get(`manage?customer_id=${viewer.customer_id}`);
          window.location.href = res.data;
        } catch (e) {
          console.log(e);
          setPending(null);
        }
      }
    },
    [viewer, get]
  );

  return isViewerLoading || !viewer ? (
    <Loading />
  ) : (
    <Box
      display="flex"
      flexDirection="column"
      flexGrow={1}
      position="relative"
      py={4}
    >
      <Box
        width="100%"
        height={200}
        bgcolor={(t) => t.palette.grey[100]}
        position="absolute"
        top={0}
        left={0}
        zIndex={0}
      />
      <Box display="flex" alignItems="end" mb={7} px={12} zIndex={1}>
        <CardMembership
          sx={{
            fontSize: 130,
            ml: '-10px',
            mr: 4,
            color: theme.palette.grey[300],
          }}
        />
        <Box display="flex" alignItems="center" gap={2}>
          <Typography variant="h1" m={0}>
            {viewer.subscription_inherited
              ? 'Your subscription is inherited as you are part of a team'
              : viewer.subscription === 'none' ||
                viewer.subscription === 'trial'
              ? 'Choose a plan'
              : `You are currently on the ${planName} plan.`}
          </Typography>
        </Box>
      </Box>

      <Box width="100%" flexGrow={1} flexShrink={0}>
        <PricingTable
          hasActivePlan={
            viewer.subscription === 'none' || viewer.subscription === 'trial'
              ? false
              : true
          }
          customerId={viewer.customer_id}
          setPlanName={setPlanName}
        />
        <Box
          display="flex"
          gap={2}
          mt={10}
          justifyContent="center"
          alignItems="center"
        >
          <Typography variant="subtitle" textAlign="center">
            Click here to
          </Typography>
          <ButtonLink
            variant="contained"
            onClick={() => onManage('manage')}
            disabled={pending === 'manage'}
            isLoading={pending === 'manage'}
            sx={{ width: 200 }}
          >
            Manage your billing info
          </ButtonLink>
        </Box>
      </Box>
    </Box>
  );
};
