import React, {
  useCallback,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from 'react';
import { Button, DialogActions, IconButton, Typography } from '@mui/material';
import { useHelpWizard } from '../../providers/HelpWizardProvider';
import { Box } from '@mui/system';
import Close from '@mui/icons-material/Close';
import { WizardStep, WizardIntro, PopoverArrow } from './HelpWizard.styled';
import { useLocation, useNavigate, Location } from 'react-router-dom';

export type HelpWizardHandle = {
  open: () => void;
  close: () => void;
  next: () => void;
  back: () => void;
};

export const HelpWizard = React.forwardRef<HelpWizardHandle, unknown>(
  (_, ref) => {
    const { steps } = useHelpWizard();
    const [step, setStep] = useState(-1);
    const [isModalOpen, setModalOpen] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();
    const origin = useRef<Location | null>(null);
    const scrollTop = useRef<number>(0);

    const handleModalClose = useCallback(
      () => setModalOpen(false),
      [setModalOpen]
    );

    const open = useCallback(() => {
      setModalOpen(true);
    }, [setModalOpen]);

    const start = useCallback(() => {
      setModalOpen(false);
      origin.current = location;
      scrollTop.current =
        document.body.scrollTop || document.documentElement.scrollTop;
      setStep(0);
    }, [setStep, location]);

    const close = useCallback(() => {
      setStep(-1);
      if (origin.current && origin.current !== location) {
        navigate(
          `${origin.current.pathname}${origin.current.search}${origin.current.hash}`
        );
      }
      window.scrollTo(0, scrollTop.current);
    }, [setStep, location, navigate]);

    const back = useCallback(
      () => setStep((prevStep) => prevStep - 1),
      [setStep]
    );

    const next = useCallback(
      () => setStep((prevStep) => prevStep + 1),
      [setStep]
    );

    useEffect(() => {
      const currentStep = step >= 0 && step < steps.length ? steps[step] : null;

      if (currentStep?.location) {
        navigate(currentStep.location);
      }

      currentStep?.element?.scrollIntoView(false);
    }, [step, steps, navigate]);

    useImperativeHandle(
      ref,
      () => ({
        open,
        close,
        next,
        back,
      }),
      [open, close, next, back]
    );

    const currentStep = step >= 0 && step < steps.length && steps[step];
    const showStep = currentStep && currentStep.element;
    const showBackButton = step > 0;
    const showNextButton = step >= 0 && step < steps.length - 1;
    const showFinishButton = step === steps.length - 1;

    return (
      <>
        {showStep && (
          <WizardStep
            open={true}
            id={currentStep.id}
            anchorEl={currentStep.element}
            anchorOrigin={currentStep.anchorOrigin}
            transformOrigin={currentStep.transformOrigin}
          >
            <PopoverArrow origin={currentStep.transformOrigin} />

            <Box display="flex">
              <Typography variant="body3">{currentStep.description}</Typography>
              <IconButton
                className="close-btn"
                edge="end"
                size="small"
                color="info"
                onClick={close}
              >
                <Close fontSize="small" />
              </IconButton>
            </Box>

            <Box
              display="flex"
              justifyContent="space-between"
              alignItems="end"
              mt={2}
            >
              <Typography className="step-index" variant="body3">
                {step + 1} / {steps.length}
              </Typography>
              <Box display="flex" gap={1}>
                {showBackButton && (
                  <Button
                    variant="outlined"
                    color="info"
                    size="small"
                    onClick={back}
                  >
                    Back
                  </Button>
                )}
                {showNextButton && (
                  <Button
                    variant="contained"
                    color="info"
                    size="small"
                    onClick={next}
                  >
                    Next
                  </Button>
                )}
                {showFinishButton && (
                  <Button
                    variant="contained"
                    color="info"
                    size="small"
                    onClick={close}
                  >
                    Got it!
                  </Button>
                )}
              </Box>
            </Box>
          </WizardStep>
        )}
        <WizardIntro open={isModalOpen} onClose={handleModalClose}>
          <IconButton className="modal-close" onClick={handleModalClose}>
            <Close />
          </IconButton>
          <Box display="flex" flexDirection="column">
            <Box className="modal-header"></Box>
            <Box className="modal-body">
              <Typography variant="body3">
                Welcome to your Bkwire account
              </Typography>
              <Typography variant="h1" pb={2}>
                Let's show you around!
              </Typography>
              <Typography variant="body2">
                Protect your business from potential losses with Bkwire's
                targeted and up-to-date corporate bankruptcy data.
              </Typography>
            </Box>
          </Box>
          <DialogActions>
            <Button variant="outlined" color="info" onClick={handleModalClose}>
              Later
            </Button>
            <Button variant="contained" color="info" onClick={start} autoFocus>
              Let's go
            </Button>
          </DialogActions>
        </WizardIntro>
      </>
    );
  }
);
