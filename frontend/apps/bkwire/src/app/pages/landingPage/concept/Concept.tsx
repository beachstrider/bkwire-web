import { useMemo } from 'react';
import { Box, Typography, Button } from '@mui/material';
import { LocalAtm, StarOutline, WorkOutline } from '@mui/icons-material';
import { ConceptRoot } from './Concept.styled';
import { useAuth0 } from '@auth0/auth0-react';

const steps = [
  {
    title: 'We do the work for you',
    subtitle:
      'Three lines of copy that describe the value of a key app feature. Make it action-oriented and simple.',
    icon: 'WorkOutline',
  },
  {
    title: 'Targeted and efficient',
    subtitle:
      'Three lines of copy that describe the value of a key app feature. Make it action-oriented and simple.',
    icon: 'StarOutline',
  },
  {
    title: 'Follow the money',
    subtitle:
      'Three lines of copy that describe the value of a key app feature. Make it action-oriented and simple.',
    icon: 'LocalAtm',
  },
];

export const Concept = () => {
  const { loginWithRedirect } = useAuth0();
  const icons = useMemo<Record<string, React.ReactNode>>(
    () => ({
      WorkOutline: <WorkOutline />,
      StarOutline: <StarOutline />,
      LocalAtm: <LocalAtm />,
    }),
    []
  );

  return (
    <ConceptRoot id="why-bkwire">
      <Typography variant="h1">
        How BK Wire
        <br /> works for your business
      </Typography>
      {steps.map((s, i) => (
        <Box className="step" key={s.title}>
          <Box className="step-nr">
            <Typography variant="h1">{i + 1}</Typography>
          </Box>
          <Box className="step-details">
            {icons[s.icon]}
            <Typography variant="h2">{s.title}</Typography>
            <Typography variant="body1">{s.subtitle}</Typography>
          </Box>
        </Box>
      ))}
      <Button
        size="large"
        variant="contained"
        onClick={() => loginWithRedirect({ screen_hint: 'signup' })}
      >
        SIGN UP TODAY
      </Button>
    </ConceptRoot>
  );
};
