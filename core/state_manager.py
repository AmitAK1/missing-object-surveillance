import config


class StateManager:
    """Manages the surveillance state and handles the alert counter."""
    
    def __init__(self, alert_threshold, return_threshold=None):
        self.state = "INITIALIZING"
        self.alert_threshold = alert_threshold
        self.missing_counter = 0

        # Grace period: object must be seen for this many consecutive frames
        # before we clear an ALERT. Prevents false recovery from tracking flicker.
        self.return_threshold = return_threshold if return_threshold is not None \
            else config.ALERT_RETURN_THRESHOLD
        self.return_counter = 0

        print("State Manager initialized.")
        print(f"Alert threshold: {alert_threshold} frames | "
              f"Return threshold: {self.return_threshold} frames.")

    def update_status(self, object_present):
        """
        Updates the state based on whether the object is present.
        Returns the current state.

        States:
          INITIALIZING → SECURED  (object seen for first time)
          SECURED      → ALERT    (object missing for alert_threshold frames)
          ALERT        → SECURED  (object present for return_threshold frames)
        """
        if self.state == "INITIALIZING" and object_present:
            self.state = "SECURED"
            self.missing_counter = 0
            self.return_counter = 0
            print("State changed to SECURED.")

        elif self.state == "SECURED":
            if not object_present:
                self.missing_counter += 1
                self.return_counter = 0  # reset grace counter
                if self.missing_counter > self.alert_threshold:
                    self.state = "ALERT"
                    print(f"State changed to ALERT! "
                          f"Object missing for {self.missing_counter} frames.")
            else:
                self.missing_counter = 0  # reset if object reappears

        elif self.state == "ALERT":
            if object_present:
                # Increment grace counter — only clear ALERT after sustained presence
                self.return_counter += 1
                if self.return_counter >= self.return_threshold:
                    self.state = "SECURED"
                    self.missing_counter = 0
                    self.return_counter = 0
                    print(f"State cleared to SECURED after "
                          f"{self.return_threshold}-frame grace period.")
            else:
                # Still missing — reset grace counter
                self.return_counter = 0

        return self.state

    def get_state(self):
        return self.state

    def get_return_progress(self):
        """Returns (return_counter, return_threshold) for UI progress display."""
        return self.return_counter, self.return_threshold