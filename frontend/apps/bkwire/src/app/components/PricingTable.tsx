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

export const PricingTable: React.VFC = () => {
  return (
    <stripe-pricing-table
      pricing-table-id={process.env.NX_APP_STRIPE_TABLE_ID || ''}
      publishable-key={process.env.NX_APP_STRIPE_TABLE_KEY || ''}
    ></stripe-pricing-table>
  );
};
