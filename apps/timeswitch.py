import appdaemon.plugins.hass.hassapi as hass
import pprint
from speaker_base import SpeakerBase


class TimeSwitch(SpeakerBase):
    def initialize(self):
        # Times, defined as a comma separated list of time_strings
        on_times = self.args.get("on_times")
        off_times = self.args.get("off_times")
        # Switches, defined as a comma separated list
        self.switches = self.split_device_list(self.args["switches"])
        self.on_phrase = self.args.get("on_phrase")
        self.off_phrase = self.args.get("off_phrase")
        pp = pprint.PrettyPrinter(depth=4)
        self.log("TimeSwitch init: {}".format(pp.pformat(self.__dict__["args"])))

        if on_times:
            for on_time in self.split_device_list(on_times):
                time = self.parse_time(on_time)
                self.run_daily(self.on_switches, time)
        if off_times:
            for off_time in self.split_device_list(off_times):
                time = self.parse_time(off_time)
                self.run_daily(self.off_switches, time)

    def off_switches(self, kwargs):
        if self.off_phrase:
            self.say_on_speakers(self.off_phrase)
        for switch in self.switches:
            self.turn_off(switch)
        self.log("turning off")

    def on_switches(self, kwargs):
        if self.on_phrase:
            self.say_on_speakers(self.on_phrase)
        for switch in self.switches:
            self.turn_on(switch)
        self.log("turning on")
