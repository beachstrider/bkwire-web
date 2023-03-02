import { useEffect, useState } from 'react';
import useApi from '../api/api.client';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Grid';
import { Typography } from '@mui/material';
import { Container } from '@mui/system';
import Button from '@mui/material/Button';

declare global {
  namespace JSX {
    interface IntrinsicElements {
      'stripe-pricing-table': React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement>,
        HTMLElement
      >;
    }
  }
}

const sptFF =
  '-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica Neue,Ubuntu,sans-serif';

export const PricingTable: React.VFC<any> = ({
  hasActivePlan,
  customerId,
  setPlanName,
}) => {
  const { get } = useApi();

  const [plans, setPlans] = useState([]);
  const [pending, setPending] = useState('');

  useEffect(() => {
    if (hasActivePlan) fetchPrices();
  }, []);

  async function fetchPrices() {
    const { data } = await get(`stripe-price-table`);
    const planName = data.find((el: any) => el.data[0].isPurhcased).data[0]
      .name;
    setPlanName(planName);
    setPlans(data);
  }

  async function updateSubscription(priceId: string) {
    setPending(priceId);
    await get(
      `subscribe?customer_id=${customerId}&price_id=${priceId}&trial=false`
    );
    await fetchPrices();
    setPending('');
  }

  return hasActivePlan ? (
    <Grid container justifyContent="center" gap={1}>
      {plans.map((plan: any, key: number) => (
        <Plan
          key={key}
          plan={plan}
          pending={pending}
          onClick={updateSubscription}
        />
      ))}
    </Grid>
  ) : (
    <stripe-pricing-table
      pricing-table-id={process.env.NX_APP_STRIPE_TABLE_ID || ''}
      publishable-key={process.env.NX_APP_STRIPE_TABLE_KEY || ''}
    ></stripe-pricing-table>
  );
};

const Plan = ({ plan: { data: el }, onClick, pending }: any) => {
  const price = el[0];

  return (
    <Grid
      item
      sx={{
        minWidth: '310px',
        padding: '34px 36px 28px',
        ...(price.metadata.most_popular == 'true'
          ? {
              border: '1px solid hsla(0,0%,10%,.1)',
              borderRadius: '12px',
              backgroundColor: 'hsla(0,0%,10%,.05)',
            }
          : {}),
      }}
    >
      <Box
        sx={{ display: 'flex', gap: 1, alignItems: 'start', height: '36px' }}
      >
        {price.metadata.most_popular == 'true' && (
          <Box
            className="stripe-plan-popular-badge"
            sx={{
              display: 'flex',
              fontSize: '12px',
              fontWeight: 500,
              color: '#545a69',
              fontFamily: sptFF,
              background: 'white',
              borderRadius: '4px',
              padding: '1px 6px',
            }}
          >
            Most popular
          </Box>
        )}
        {price.livemode === false && (
          <Box
            sx={{
              display: 'flex',
              fontSize: '12px',
              fontWeight: 500,
              color: '#983705',
              backgroundColor: '#ffde92',
              fontFamily: sptFF,
              borderRadius: '4px',
              padding: '1px 6px',
            }}
          >
            TEST MODE
          </Box>
        )}
      </Box>
      <Typography
        variant="h3"
        color="black"
        fontWeight={500}
        sx={{ marginBottom: '12px', fontSize: '20px', fontFamily: sptFF }}
      >
        {price.name}
      </Typography>
      <Typography
        variant="body2"
        color="#1a1a1a"
        sx={{
          opacity: 0.5,
          fontFamily: sptFF,
          fontSize: '14px',
          marginBottom: '32px',
        }}
      >
        {price.description}
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <Typography
          color="#1a1a1a"
          sx={{ fontSize: '36px', fontWeight: 700, fontFamily: sptFF }}
        >
          {new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 2,
          }).format(price.unit_amount / 100)}
        </Typography>
        <Typography
          color="#1a1a1a"
          sx={{ fontSize: '13px', opacity: 0.5, marginLeft: '3px' }}
        >
          per
          <br />
          month
        </Typography>
      </Box>
      {price.isPurhcased ? (
        <Button
          variant="text"
          disableElevation
          fullWidth
          size="large"
          sx={{ borderRadius: '6px', marginTop: '16px' }}
        >
          Subscribed
        </Button>
      ) : (
        <Button
          variant="contained"
          disableElevation
          fullWidth
          size="large"
          disabled={pending === price.default_price}
          sx={{ borderRadius: '6px', marginTop: '16px' }}
          onClick={() => onClick(price.default_price)}
        >
          Subscribe
        </Button>
      )}
      <Typography
        color="#1a1a1a"
        sx={{ margin: '12px 0', fontSize: '14px', fontFamily: sptFF }}
      >
        This includes:
      </Typography>
      <Box>
        {price.features.split(', ').map((feature: string, key: number) => (
          <Box
            key={key}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: '9px',
              marginBottom: '6px',
            }}
          >
            <svg
              className="InlineSVG Icon PriceColumn-check Icon--sm"
              focusable="false"
              fill="#1a1a1a"
              color="#1a1a1a"
              fillOpacity="0.5"
              height={12}
              viewBox="0 0 16 16"
              width={16}
            >
              <path
                d="m8 16c-4.418278 0-8-3.581722-8-8s3.581722-8 8-8 8 3.581722 8 8-3.581722 8-8 8zm3.0832728-11.00479172-4.0832728 4.09057816-1.79289322-1.79289322c-.39052429-.39052429-1.02368927-.39052429-1.41421356 0s-.39052429 1.02368927 0 1.41421356l2.5 2.50000002c.39052429.3905243 1.02368927.3905243 1.41421356 0l4.79037962-4.79768495c.3905243-.3905243.3905243-1.02368927 0-1.41421357-.3905243-.39052429-1.0236893-.39052429-1.4142136 0z"
                fillRule="evenodd"
              />
            </svg>
            <Typography
              color="#1a1a1a"
              sx={{ fontSize: '14px', fontFamily: sptFF }}
            >
              {feature}
            </Typography>
          </Box>
        ))}
      </Box>
    </Grid>
  );
};
