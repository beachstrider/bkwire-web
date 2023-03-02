import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import {
  ThemeProvider,
  LocalizationProvider,
  QueryClientProvider,
  AuthProvider,
  HelpWizardProvider,
} from './providers';
import { RequireAuth } from './components/auth/RequireAuth';
import { Header } from './layout/header/Header';
import { Footer } from './layout/footer/Footer';
import { Dashboard } from './pages/dashboard/Dashboard';
import { List } from './pages/list/List';
import { Watchlist } from './pages/watchlist/Watchlist';
import { Account } from './pages/account/Account';
import { View } from './pages/view/View';
import { LandingPage } from './pages/landingPage/LandingPage';
import { Onboarding } from './pages/onboarding/Onboarding';
import { Notifications } from './pages/notifications/Notifications';
import { AppContainer, AppRoot } from './app.styled';
import { SnackbarProvider } from 'notistack';
import { News } from './pages/news/News';

import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';

import '../styles/global.css';

const App = () => (
  <ThemeProvider>
    <LocalizationProvider>
      <QueryClientProvider>
        <Router>
          <AuthProvider>
            <SnackbarProvider>
              <HelpWizardProvider>
                <AppRoot className="app">
                  <Header />
                  <AppContainer maxWidth="lg">
                    <Routes>
                      <Route index element={<LandingPage />} />
                      <Route
                        path="dashboard"
                        element={
                          <RequireAuth>
                            <Dashboard />
                          </RequireAuth>
                        }
                      />
                      <Route
                        path="onboarding/*"
                        element={
                          <RequireAuth>
                            <Onboarding />
                          </RequireAuth>
                        }
                      />
                      <Route
                        path="account/*"
                        element={
                          <RequireAuth>
                            <Account />
                          </RequireAuth>
                        }
                      />
                      <Route
                        path="list/*"
                        element={
                          <RequireAuth>
                            <List />
                          </RequireAuth>
                        }
                      />
                      <Route
                        path="view/*"
                        element={
                          <RequireAuth>
                            <View />
                          </RequireAuth>
                        }
                      />
                      <Route
                        path="watchlist/*"
                        element={
                          <RequireAuth>
                            <Watchlist />
                          </RequireAuth>
                        }
                      />
                      <Route
                        path="notifications/*"
                        element={
                          <RequireAuth>
                            <Notifications />
                          </RequireAuth>
                        }
                      />
                      <Route
                        path="news/*"
                        element={
                          <RequireAuth>
                            <News />
                          </RequireAuth>
                        }
                      />
                      <Route path="auth/login" element={<RequireAuth />} />
                      <Route path="*" element={<div>Not found</div>} />
                    </Routes>
                  </AppContainer>
                  <Footer />
                </AppRoot>
              </HelpWizardProvider>
            </SnackbarProvider>
          </AuthProvider>
        </Router>
      </QueryClientProvider>
    </LocalizationProvider>
  </ThemeProvider>
);

export default App;
