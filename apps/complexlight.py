import movementlight as movementlight
MovementLight = movementlight.MovementLight

class ComplexLight(MovementLight):
    def initialize(self):
        self.switch = self.args['switch']
        MovementLight.initialize(self)
        self.log("Initializing complex light: {} motion: {} timeout: {} use_sun: {}"
                 .format(self.light, self.motion, self.timeout, self.use_sun))

    def on_timeout(self, *args):
        switch_state = self.get_state(self.switch)
        motion_state = self.get_state(self.motion)
        self.log("switch: {}, motion: {}".format(switch_state, motion_state))
        if MovementLight.get_motion_state():
            self.log("off blocked")
            self.timeout_handler = self.run_in(self.on_timeout, self.timeout)
        else:
            self.log("off triggered")
            self.turn_off(self.light)
