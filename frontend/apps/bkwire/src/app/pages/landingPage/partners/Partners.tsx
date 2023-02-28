import { Box, useTheme } from '@mui/material';
import { Slider } from '../../../components/slider/Slider';
import { PartnerCard, PartnersRoot } from './Partners.styled';
import logoAeganAirlines from '../../../../assets/partner-logos/logo-aeganairlines.png';
import logoApplebees from '../../../../assets/partner-logos/logo-applebees.png';
import logoEvernote from '../../../../assets/partner-logos/logo-evernote.png';
import logoFilmax from '../../../../assets/partner-logos/logo-filmax.png';
import logoHago from '../../../../assets/partner-logos/logo-hago.png';
import logoJhonsonControls from '../../../../assets/partner-logos/logo-jhonsoncontrols.png';
import logoMsn from '../../../../assets/partner-logos/logo-msn.png';
import logoPananna from '../../../../assets/partner-logos/logo-pananna.png';
import logoPicasa from '../../../../assets/partner-logos/logo-picasa.png';
import logoSixFlags from '../../../../assets/partner-logos/logo-sixflags.png';
import logoTwinField from '../../../../assets/partner-logos/logo-twinfield.png';

const partners = [
  { name: 'Airlines', logo: logoAeganAirlines },
  { name: 'Applebees', logo: logoApplebees },
  { name: 'Evernote', logo: logoEvernote },
  { name: 'Filmax', logo: logoFilmax },
  { name: 'Hago', logo: logoHago },
  { name: 'Jhonson Controls', logo: logoJhonsonControls },
  { name: 'MSN', logo: logoMsn },
  { name: 'Pananna', logo: logoPananna },
  { name: 'Picasa', logo: logoPicasa },
  { name: 'Six Flags', logo: logoSixFlags },
  { name: 'Twin Field', logo: logoTwinField },
];

export const Partners = () => {
  const theme = useTheme();

  return (
    <PartnersRoot>
      <Box>
        <Slider
          autoplay={10000}
          minHeight={130}
          gap={theme.spacing(2)}
          responsive={[
            {
              itemsPerPage: 4,
              transitionDuration: 300,
              showPagination: false,
              showControls: true,
            },
          ]}
        >
          {partners.map((p) => (
            <PartnerCard key={p.name} logo={p.logo}>
              <Box></Box>
            </PartnerCard>
          ))}
        </Slider>
      </Box>
    </PartnersRoot>
  );
};
