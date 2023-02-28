import { FormatQuoteRounded } from '@mui/icons-material';
import { Box, Typography } from '@mui/material';
import { Slider } from '../../../components/slider/Slider';
import { Quote } from './Quotes.styled';

const quotes = [
  {
    author: 'First Lastname',
    title: 'Title/descriptor',
    text: `
      A nice long testimonial quote can go here. There is sufficient
      space for a testimonial to wrap maximum 5 lines. Keep in mind
      that testimonials should be exciting and emphasize the value of
      the platform. They should also be relatable with an eye to
      influencing positive conversion rates on the site.
    `,
  },
  {
    author: 'First Lastname',
    title: 'Title/descriptor',
    text: `
      A nice long testimonial quote can go here. There is sufficient
      space for a testimonial to wrap maximum 5 lines. Keep in mind
      that testimonials should be exciting and emphasize the value of
      the platform. They should also be relatable with an eye to
      influencing positive conversion rates on the site.
    `,
  },
  {
    author: 'First Lastname',
    title: 'Title/descriptor',
    text: `
      A nice long testimonial quote can go here. There is sufficient
      space for a testimonial to wrap maximum 5 lines. Keep in mind
      that testimonials should be exciting and emphasize the value of
      the platform. They should also be relatable with an eye to
      influencing positive conversion rates on the site.
    `,
  },
  {
    author: 'First Lastname',
    title: 'Title/descriptor',
    text: `
      A nice long testimonial quote can go here. There is sufficient
      space for a testimonial to wrap maximum 5 lines. Keep in mind
      that testimonials should be exciting and emphasize the value of
      the platform. They should also be relatable with an eye to
      influencing positive conversion rates on the site.
    `,
  },
];

export const Quotes = () => {
  return (
    <Box position="relative">
      <Slider autoplay={6000} paginationPosition={{ left: 130, bottom: 70 }}>
        {quotes.map((quote) => (
          <Quote key={quote.author}>
            <Box>
              <FormatQuoteRounded fontSize="large" />
            </Box>
            <Box flexGrow={1}>
              <Typography variant="body1">{quote.text}</Typography>
              <Typography variant="body2" fontWeight="bold" mt={2}>
                {quote.author}
              </Typography>
              <Typography variant="body3">{quote.title}</Typography>
            </Box>
          </Quote>
        ))}
      </Slider>
    </Box>
  );
};
