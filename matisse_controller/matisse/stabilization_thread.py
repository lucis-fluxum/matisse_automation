import threading
import time
from queue import Queue

import matisse_controller.config as cfg
from matisse_controller.matisse.event_report import log_event


class StabilizationThread(threading.Thread):
    def __init__(self, matisse, messages: Queue, *args, **kwargs):
        """
        Parameters
        ----------
        matisse : matisse_controller.matisse.matisse.Matisse
        messages
            a message queue
        *args
            args to pass to `Thread.__init__`
        **kwargs
            kwargs to pass to `Thread.__init__`
        """
        super().__init__(*args, **kwargs)
        self._matisse = matisse
        self.messages = messages
        # Stop any running scans just in case
        self._matisse.stop_scan()
        self._matisse.query(f"SCAN:RISINGSPEED {cfg.get(cfg.STABILIZATION_RISING_SPEED)}")
        self._matisse.query(f"SCAN:FALLINGSPEED {cfg.get(cfg.STABILIZATION_FALLING_SPEED)}")

    def run(self):
        """
        Try to keep the measured wavelength within the configured tolerance by scanning the reference cell.

        Exit if anything is pushed to the message queue.
        """
        while True:
            if self.messages.qsize() == 0:
                current_wavelength = self._matisse.wavemeter_wavelength()
                drift = self._matisse.target_wavelength - current_wavelength
                drift = round(drift, cfg.get(cfg.WAVEMETER_PRECISION))
                if abs(drift) > cfg.get(cfg.STABILIZATION_TOLERANCE):
                    if drift < 0:
                        # measured wavelength is too high
                        print(f"Wavelength too high, decreasing. Drift is {drift} nm.")
                        if not self._matisse.is_any_limit_reached():
                            if cfg.get(cfg.REPORT_EVENTS):
                                log_event('wavelength_drift', self._matisse, current_wavelength,
                                          f"wavelength drifted by {drift} nm")
                            self._matisse.start_scan(self._matisse.SCAN_MODE_DOWN)
                        else:
                            self.do_stabilization_correction(current_wavelength, drift)
                    else:
                        # measured wavelength is too low
                        print(f"Wavelength too low, increasing.  Drift is {drift} nm.")
                        if not self._matisse.is_any_limit_reached():
                            if cfg.get(cfg.REPORT_EVENTS):
                                log_event('wavelength_drift', self._matisse, current_wavelength,
                                          f"wavelength drifted by {drift} nm")
                            self._matisse.start_scan(self._matisse.SCAN_MODE_UP)
                        else:
                            self.do_stabilization_correction(current_wavelength, drift)
                else:
                    self._matisse.stop_scan()
                    # print(f"Within tolerance. Drift is {drift}")
                time.sleep(cfg.get(cfg.STABILIZATION_DELAY))
            else:
                self._matisse.stop_scan()
                break

    def do_stabilization_correction(self, wavelength, drift):
        """Reset the stabilization piezos and optionally log the correction event."""
        print('WARNING: A component has hit a limit while adjusting the RefCell. Attempting automatic corrections.')
        self._matisse.stop_scan()
        if cfg.get(cfg.REPORT_EVENTS):
            log_event('stabilization_correction', self._matisse, wavelength,
                      'component hit a limit while auto-stabilization was on')
        self._matisse.reset_stabilization_piezos()
        self._matisse.stabilization_auto_corrections += 1
