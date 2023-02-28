import { styled, Box, Typography } from '@mui/material';

export const SidebarBg = ({
  bgImg,
  title,
}: {
  bgImg: string;
  title: React.ReactNode;
}) => (
  <Box
    display="flex"
    justifyContent="end"
    flexShrink={0}
    width={470}
    textAlign="right"
    p={6}
    pr={8}
    css={{
      backgroundImage: `url(${bgImg})`,
      backgroundSize: 'cover',
      textShadow: '-1px 1px 1px rgba(0,0,0,0.5)',
    }}
  >
    <Typography variant="greeting" color="white">
      {title}
    </Typography>
  </Box>
);

export const SpecialHint = styled(Box)`
  border-radius: 6px;
  color: rgb(255, 226, 183);
  background-color: rgb(25, 18, 7);
  padding: ${(p) => p.theme.spacing(2)};

  h3,
  strong {
    color: rgb(255, 167, 38);
  }
`;
