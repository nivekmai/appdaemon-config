import appdaemon.plugins.hass.hassapi as hass


class ZwaveAdd(hass.Hass):
    def initialize(self):
        self.light = self.args["light"]
        self.motion = self.args["motion"]
        self.timeout = self.args["timeout"]
        self.timeout_handler = None
        self.log(
            "Initializing motion sensor light: {} motion: {} timeout: {}".format(
                self.light, self.motion, self.timeout
            )
        )
        self.listen_state(self.on_motion, self.motion)

    def on_motion(self, entity, attribute, old, new, kwargs):
        self.log("INFO: motion state changed ({})".format(new))
        if self.sun_down() and new == "on":
            self.log("INFO: motion on and sun_down")
            if self.timeout_handler is not None:
                self.log("INFO: timer exists, resetting")
                self.timeout_handler = self.cancel_timer(self.timeout_handler)
            self.turn_on(self.light)
            self.timeout_handler = self.run_in(self.on_timeout, self.timeout)

    def on_timeout(self, *args):
        # if the motion sensor is still on, don't turn off just yet
        if self.get_state(self.motion) is "on":
            self.log(
                "{} is still detecting movement (state: {}), not turning off the light".format(
                    self.motion, self.get_state(self.motion)
                )
            )
            self.timeout_handler = self.run_in(self.on_timeout, self.timeout)
        else:
            self.log("no movement, turning off")
            self.turn_off(self.light)
