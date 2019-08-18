import appdaemon.plugins.hass.hassapi as hass


class DoorLight(hass.Hass):
    def initialize(self):
        self.light = self.args["light"]
        self.door = self.args["door"]
        self.use_sun = self.args.get('use_sun', 'true') == 'true'
        self.timeout = self.args.get('timeout', 0)
        self.timer_handle = None
        self.log("Initializing door light: {} door: {} use_sun: {} timeout: {}"
                 .format(self.light, self.door, self.use_sun, self.timeout))
        self.listen_state(self.on_door_change, self.door)

    def on_door_change(self, entity, attribute, old, new, kwargs):
        self.log("INFO: door state changed ({})".format(new))
        if self.timer_handle:
            self.cancel_timer(self.timer_handle)
        if (self.use_sun and self.sun_down() or not self.use_sun):
            if (new == "on"):
                self.log("INFO: door off (open) and sun_down")
                self.turn_on(self.light)
            else:
                self.log("INFO: door on (closed) and sun_down")
                self.timer_handle = self.run_in(self.turn_off_light, self.timeout)

    def turn_off_light(self, *args):
        self.cancel_timer(self.timer_handle)
        self.turn_off(self.light)
        self.log("INFO: runing off light {}".format(self.light))

