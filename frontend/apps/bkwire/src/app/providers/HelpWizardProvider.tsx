import React, {
  useMemo,
  createContext,
  useContext,
  useState,
  useRef,
} from 'react';
import { PopoverOrigin } from '@mui/material';
import {
  HelpWizard,
  HelpWizardHandle,
} from '../components/helpWizard/HelpWizard';

interface HelpWizardStep {
  id: string;
  description: string;
  element: Element | null;
  anchorOrigin: PopoverOrigin | undefined;
  transformOrigin: PopoverOrigin | undefined;
  location?: string;
}
interface HelpWizardContextType {
  steps: HelpWizardStep[];

  wizard: React.MutableRefObject<HelpWizardHandle | null>;

  setHomeElement: React.Dispatch<React.SetStateAction<Element | null>>;
  setAllBksElement: React.Dispatch<React.SetStateAction<Element | null>>;
  setAllLossesElement: React.Dispatch<React.SetStateAction<Element | null>>;
  setWatchlistElement: React.Dispatch<React.SetStateAction<Element | null>>;
  setNotificationsElement: React.Dispatch<React.SetStateAction<Element | null>>;
  // setNewsElement: React.Dispatch<React.SetStateAction<Element | null>>;
  // setTodayGridElement: React.Dispatch<React.SetStateAction<Element | null>>;
  setHelpElement: React.Dispatch<React.SetStateAction<Element | null>>;
}
const HelpWizardContext = createContext<HelpWizardContextType>(
  {} as HelpWizardContextType
);

export const HelpWizardProvider: React.FC = ({ children }): JSX.Element => {
  const [homeElement, setHomeElement] = useState<Element | null>(null);
  const [allBksElement, setAllBksElement] = useState<Element | null>(null);
  const [allLossesElement, setAllLossesElement] = useState<Element | null>(
    null
  );
  const [watchlistElement, setWatchlistElement] = useState<Element | null>(
    null
  );
  const [notificationsElement, setNotificationsElement] =
    useState<Element | null>(null);
  // const [newsElement, setNewsElement] = useState<Element | null>(null);
  // const [todayGridElement, setTodayGridElement] = useState<Element | null>(
  //   null
  // );
  const [helpElement, setHelpElement] = useState<Element | null>(null);

  const wizardRef = useRef<HelpWizardHandle | null>(null);

  const value = useMemo(
    () => ({
      steps: [
        {
          id: 'home-wizard-step',
          description:
            'Find the latest insights, trends, and news about corporate bankruptcies and related losses taken on by investors.',
          element: homeElement,
          anchorOrigin: {
            vertical: 60,
            horizontal: 'left',
          },
          transformOrigin: {
            vertical: 'top',
            horizontal: 'left',
          },
        },
        {
          id: 'bl-wizard-step',
          description:
            'Search and follow any corporate bankruptcy case in our up-to-date database.',
          element: allBksElement,
          anchorOrigin: {
            vertical: 60,
            horizontal: 'left',
          },
          transformOrigin: {
            vertical: 'top',
            horizontal: 'left',
          },
        },
        {
          id: 'bl-wizard-step',
          description: 'Search and follow any loss in our up-to-date database.',
          element: allLossesElement,
          anchorOrigin: {
            vertical: 60,
            horizontal: 'left',
          },
          transformOrigin: {
            vertical: 'top',
            horizontal: 'left',
          },
        },
        {
          id: 'watchlist-wizard-step',
          description:
            'Keep track of companies with losses and bankruptcies that you are following.',
          element: watchlistElement,
          anchorOrigin: {
            vertical: 60,
            horizontal: 'left',
          },
          transformOrigin: {
            vertical: 'top',
            horizontal: 'left',
          },
        },
        {
          id: 'notifications-wizard-step',
          description:
            'Get notifications about companies and bankruptcies you are following, and manage your notification settings.',
          element: notificationsElement,
          anchorOrigin: {
            vertical: 74,
            horizontal: 'right',
          },
          transformOrigin: {
            vertical: 'top',
            horizontal: 'right',
          },
        },
        // {
        //   id: 'news-wizard-step',
        //   description:
        //     'Get the latest news about losses and cororate bankruptcy activity.',
        //   element: newsElement,
        //   anchorOrigin: {
        //     vertical: -8,
        //     horizontal: 'right',
        //   },
        //   transformOrigin: {
        //     vertical: 'bottom',
        //     horizontal: 'right',
        //   },
        //   location: '/dashboard',
        // },
        // {
        //   id: 'today-grid-wizard-step',
        //   description:
        //     'Dig deeper into any bankruptcy or company, and add to your watchlist to follow and track their activity.',
        //   element: todayGridElement,
        //   anchorOrigin: {
        //     vertical: 93,
        //     horizontal: 'right',
        //   },
        //   transformOrigin: {
        //     vertical: 'bottom',
        //     horizontal: 'right',
        //   },
        //   location: '/dashboard',
        // },
        {
          id: 'help-wizard-step',
          description:
            'Need a little refresher or some help? Find this tour anytime, and access our help topics.',
          element: helpElement,
          anchorOrigin: {
            vertical: 74,
            horizontal: 'right',
          },
          transformOrigin: {
            vertical: 'top',
            horizontal: 'right',
          },
        },
      ] as HelpWizardStep[],

      wizard: wizardRef,

      setHomeElement,
      setAllBksElement,
      setAllLossesElement,
      setWatchlistElement,
      setNotificationsElement,
      // setNewsElement,
      // setTodayGridElement,
      setHelpElement,
    }),
    [
      homeElement,
      allBksElement,
      allLossesElement,
      watchlistElement,
      notificationsElement,
      // newsElement,
      // todayGridElement,
      helpElement,

      wizardRef,

      setHomeElement,
      setAllBksElement,
      setAllLossesElement,
      setWatchlistElement,
      setNotificationsElement,
      // setNewsElement,
      // setTodayGridElement,
      setHelpElement,
    ]
  );

  return (
    <HelpWizardContext.Provider value={value}>
      {children}
      <HelpWizard ref={wizardRef} />
    </HelpWizardContext.Provider>
  );
};

export const useHelpWizard = () => useContext(HelpWizardContext);
export default HelpWizardProvider;
