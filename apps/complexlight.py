import movementlight as movementlight

MovementLight = movementlight.MovementLight


class ComplexLight(MovementLight):
    def initialize(self):
        self.switch = self.args["switch"]
        MovementLight.initialize(self)
        self.log(
            "Initializing complex light: {} motion: {} timeout: {} use_sun: {}".format(
                self.light, self.motion, self.timeout, self.use_sun
            )
        )
        self.listen_state(self.on_switch, self.switch)

    def on_switch(self, entity, attribute, old, new, kwargs):
        self.log("switch state changed ({})".format(new))
        if (self.use_sun and self.sun_down() or not self.use_sun) and (
            new == "on" or new == "active"
        ):
            self.log("switch on and sun_down")
            self.activate()
        if new == "off" and self.timeout_handler is None:
            self.deactivate()

    def on_timeout(self, *args):
        self.log("on timeout triggered")
        switch_state = self.get_state(self.switch)
        motion_state = self.get_motion_state()
        self.log("switch: {}, motion: {}".format(switch_state, motion_state))
        if motion_state or switch_state == "on":
            self.log("off blocked")
            self.timeout_handler = self.run_in(self.on_timeout, self.timeout)
        else:
            self.log("off triggered")
            self.deactivate()
