class StateManager:
    """Manages the surveillance state and handles the alert counter."""
    
    def __init__(self, alert_threshold):
        self.state = "INITIALIZING"
        self.alert_threshold = alert_threshold
        self.missing_counter = 0
        print("State Manager initialized.")
        print(f"Alert threshold set to {alert_threshold} frames.")

    def update_status(self, object_present):
        """
        Updates the state based on whether the object is present.
        Returns the current state.
        """
        if self.state == "INITIALIZING" and object_present:
            self.state = "SECURED"
            self.missing_counter = 0
            print("State changed to SECURED.")

        elif self.state == "SECURED":
            if not object_present:
                self.missing_counter += 1
                if self.missing_counter > self.alert_threshold:
                    self.state = "ALERT"
                    print(f"State changed to ALERT! Object missing for {self.missing_counter} frames.")
            else:
                self.missing_counter = 0 # Reset counter if object reappears

        elif self.state == "ALERT":
            if object_present:
                # Object has returned
                self.state = "SECURED"
                self.missing_counter = 0
                print("State changed back to SECURED. Object has returned.")
        
        return self.state

    def get_state(self):
        return self.state