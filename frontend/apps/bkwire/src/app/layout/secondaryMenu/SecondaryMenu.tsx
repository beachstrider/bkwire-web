import React, { useCallback, useEffect, useState } from 'react';
import { Box, Tab, ClickAwayListener, Badge } from '@mui/material';
import AccountCircle from '@mui/icons-material/AccountCircle';
import HelpIcon from '@mui/icons-material/Help';
import NotificationsIcon from '@mui/icons-material/Notifications';
import { MenuTabs } from './SecondaryMenu.styled';
import { HelpMenu } from './HelpMenu';
import {
  HEADER_NOTIFICATION_FILTERS,
  NotificationsMenu,
} from './NotificationsMenu';
import { ProfileMenu } from './ProfileMenu';
import { useHelpWizard } from '../../providers/HelpWizardProvider';
import { usePrevious } from '../../hooks/usePrevious';
import {
  useGetUnreadNotifications,
  useGetViewer,
  useReadNotifications,
  useUpdateUser,
} from '../../api/api.hooks';
import { VideoPopup, VideoType } from './VideoPopup';

enum Tabs {
  None = -1,
  Help = 0,
  Notifications = 1,
  Profile = 2,
}

export const SecondaryMenu = () => {
  const { data: viewer } = useGetViewer();
  const { mutate: updateViewer } = useUpdateUser();

  const { mutate: readNotifications } = useReadNotifications();
  const [tab, setTab] = React.useState(Tabs.None);
  const prevTab = usePrevious(tab);
  const { wizard, setNotificationsElement, setHelpElement } = useHelpWizard();
  const { data: unreadCount } = useGetUnreadNotifications();

  const [videoType, setVideoType] = useState<VideoType>('tour');
  const [isVideoModalOpen, setIsVideoModalOpen] = useState(false);

  const close = useCallback(() => {
    if (tab === Tabs.Notifications) {
      readNotifications(HEADER_NOTIFICATION_FILTERS);
    }
    setTab(Tabs.None);
  }, [readNotifications, tab]);

  const onTabChange = useCallback(
    (_, t) => {
      if (tab === Tabs.Notifications) {
        readNotifications(HEADER_NOTIFICATION_FILTERS);
      }
      setTab(t);
    },
    [readNotifications, tab]
  );

  const openHelpWizard = useCallback(() => {
    if (wizard.current) {
      wizard.current.open();
      setTab(Tabs.None);
    }
  }, [wizard]);

  const openVideoPopup = useCallback(
    (type: VideoType) => {
      setVideoType(type);
      setIsVideoModalOpen(true);
    },
    [setIsVideoModalOpen]
  );

  const handleVideoPopupClose = useCallback(() => {
    if (
      viewer &&
      viewer.tos &&
      viewer.onboarding_completed &&
      viewer.product_tour_enabled
    ) {
      updateViewer({
        id: viewer.id,
        product_tour_enabled: 0,
      });
    }
    setIsVideoModalOpen(false);
  }, [updateViewer, viewer]);

  useEffect(() => {
    if (
      viewer &&
      viewer.tos &&
      viewer.onboarding_completed &&
      viewer.product_tour_enabled
    ) {
      setIsVideoModalOpen(true);
    }
  }, [viewer]);

  return (
    <>
      <ClickAwayListener onClickAway={close}>
        <Box>
          <MenuTabs
            noTransition={tab === Tabs.None || prevTab === Tabs.None}
            textColor="inherit"
            value={tab}
            onChange={onTabChange}
          >
            <Tab disabled value={Tabs.None} />
            <Tab value={Tabs.Help} icon={<HelpIcon />} ref={setHelpElement} />
            <Tab
              value={Tabs.Notifications}
              sx={{ overflow: 'visible' }}
              icon={
                <Badge
                  color="error"
                  variant="standard"
                  showZero={false}
                  badgeContent={unreadCount ?? 0}
                  max={999}
                >
                  <NotificationsIcon />
                </Badge>
              }
              ref={setNotificationsElement}
            />
            <Tab value={Tabs.Profile} icon={<AccountCircle />} />
          </MenuTabs>

          {tab === Tabs.Help && (
            <HelpMenu
              close={close}
              openHelpWizard={openHelpWizard}
              openVideoPopup={openVideoPopup}
            />
          )}
          {tab === Tabs.Notifications && <NotificationsMenu close={close} />}
          {tab === Tabs.Profile && <ProfileMenu close={close} />}
        </Box>
      </ClickAwayListener>
      <VideoPopup
        type={videoType}
        open={isVideoModalOpen}
        onClose={handleVideoPopupClose}
      />
    </>
  );
};
