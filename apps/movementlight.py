import appdaemon.plugins.hass.hassapi as hass


class MovementLight(hass.Hass):
    def initialize(self):
        self.light = self.args.get("light", "")
        self.motion = self.split_device_list(self.args["motion"])
        self.timeout = self.args.get("timeout", 120)
        self.use_sun = self.args.get("use_sun", "true") == "true"
        self.delay = self.args.get("delay", 0)
        self.timeout_handler = None
        self.delay_handler = None
        self.log(
            "Initializing motion sensor light: {} motion: {} timeout: {} use_sun: {} delay: {}".format(
                self.light, self.motion, self.timeout, self.use_sun, self.delay
            )
        )
        for motion in self.motion:
            self.log("listening to: {}".format(motion))
            self.listen_state(self.on_motion, motion)

    def on_motion(self, entity, attribute, old, new, kwargs):
        self.log("motion state changed ({})".format(new))
        if (self.use_sun and self.sun_down() or not self.use_sun) and (
            new == "on" or new == "active"
        ):
            self.log("motion on and sun_down")
            if self.delay != 0:
                if self.delay_handler is not None:
                    self.delay_handler = self.cancel_timer(self.delay_handler)
                self.delay_handler = self.run_in(self.after_delay, self.delay)
            else:
                self.restart_and_activate()

    def restart_and_activate(self):
        self.log("restart_and_activate")
        if self.timeout_handler is not None:
            self.log("timer exists, resetting")
            self.timeout_handler = self.cancel_timer(self.timeout_handler)
        self.activate()
        if self.timeout != 0:
            self.log("setting timeout")
            self.timeout_handler = self.run_in(self.on_timeout, self.timeout)

    def after_delay(self, *_):
        self.log("after delay")
        if (
            self.use_sun and self.sun_down() or not self.use_sun
        ) and self.get_motion_state():
            self.log("starting after delay")
            self.restart_and_activate()

    def activate(self):
        self.log("movement light activating")
        self.turn_on(self.light)

    def deactivate(self):
        self.log("movement light deactivating")
        self.timeout_handler = None
        self.turn_off(self.light)

    def on_timeout(self, *_):
        self.log("on timeout")
        # if the motion sensor is still on, don't turn off just yet
        if self.get_motion_state():
            self.log(
                "{} is still detecting movement (state: {}),"
                "not turning off the light".format(self.motion, self.get_motion_state())
            )
            self.timeout_handler = self.run_in(self.on_timeout, self.timeout)
        else:
            self.log("no movement, turning off")
            self.deactivate()

    def get_motion_state(self, *_):
        for motion in self.motion:
            self.log("motion {}".format(self.get_state(motion)))
            if self.get_state(motion) == "on" or self.get_state(motion) == "active":
                return True
        return False
