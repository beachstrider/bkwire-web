import { createTheme } from '@mui/material/styles';
import getLayout from './theme.layout';
import getPalette from './theme.palette';
import getTypography from './theme.typography';
import getTransitions from './theme.transitions';
import getZIndex from './theme.depth';
import getCustom from './theme.custom';
import getComponents from './theme.components';

let theme = createTheme();

theme = createTheme(theme, { ...getLayout(theme) });
theme = createTheme(theme, { palette: getPalette(theme) });
theme = createTheme(theme, { typography: getTypography(theme) });
theme = createTheme(theme, { transitions: getTransitions(theme) });
theme = createTheme(theme, { zIndex: getZIndex(theme) });
theme = createTheme(theme, { ...getCustom(theme) });
theme = createTheme(theme, { components: getComponents(theme) });

export default theme;
