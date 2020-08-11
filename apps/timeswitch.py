import appdaemon.plugins.hass.hassapi as hass


class TimeSwitch(hass.Hass):
    def initialize(self):
        # Times, defined as a comma separated list of time_string s
        on_times = self.split_device_list(self.args["on_times"])
        off_times = self.split_device_list(self.args["off_times"])
        # Switches, defined as a comma separated list
        self.switches = self.split_device_list(self.args["switches"])
        self.speakers = self.split_device_list(self.args.get("speakers", ""))
        self.on_phrase = self.args.get("on_phrase")
        self.off_phrase = self.args.get("off_phrase")
        self.log("TimeSwitch init: {}".format(self.__dict__))

        for on_time in on_times:
            time = self.parse_time(on_time)
            self.run_daily(self.on_switches, time)
        for off_time in off_times:
            time = self.parse_time(off_time)
            self.run_daily(self.off_switches, time)

    def off_switches(self, kwargs):
        if self.off_phrase:
            for speaker in self.speakers:
                self.call_service(
                    "tts/google_say", entity_id=speaker, message=self.off_phrase
                )
        for switch in self.switches:
            self.turn_off(switch)
        self.log("turning off")

    def on_switches(self, kwargs):
        if self.on_phrase:
            for speaker in self.speakers:
                self.call_service(
                    "tts/google_say", entity_id=speaker, message=self.on_phrase
                )
        for switch in self.switches:
            self.turn_on(switch)
        self.log("turning on")
