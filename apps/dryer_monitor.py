import appdaemon.plugins.hass.hassapi as hass
import datetime
import math
from speaker_base import SpeakerBase


class DryerMonitor(SpeakerBase):
    def initialize(self):
        self.state_sensor = self.args.get("state_sensor", "sensor.dryer_state")
        self.time_sensor = self.args.get("time_sensor", "sensor.dryer_time")
        self.power_sensor = self.args.get("power_sensor", "sensor.dryer_power")
        self.power_low = float(self.args.get("power_low", "300"))
        self.finish_phrase = self.args.get("finish_phrase", "The dryer has finished")
        self.power_state = "off"
        self.set_power_state("off")
        self.log("PowerMonitor init: {}".format(self.__dict__))
        self.listen_state(self.on_sensor_change, self.power_sensor)
        self.run_minutely(self.on_minute, datetime.time(0, 0, 0))

    def set_power_state(self, state):
        self.power_state = state
        self.set_state(self.state_sensor, state=state)

    def set_time_state(self, state):
        self.set_state(self.time_sensor, state=state)

    def get_remaining_minutes(self):
        started = self.get_state(self.state_sensor, attribute="last_changed")
        started_ts = self.convert_utc(started).replace()
        diff = datetime.datetime.now(started_ts.tzinfo) - started_ts
        remaining = math.floor(
            ((datetime.timedelta(minutes=90) - diff).total_seconds() / 60)
        )
        return remaining

    def on_minute(self, *args):
        if self.power_state == "on":
            remaining = self.get_remaining_minutes()
            self.log("remaining: {}".format(remaining))
            self.set_time_state("{}m".format(remaining))
        else:
            self.set_time_state("off")

    def on_sensor_change(self, entity, attribute, old, new, kwargs):
        new = float(new)
        if new > self.power_low:
            self.set_power_state("on")
        elif new == 0 and self.power_state == "on":
            self.set_power_state("off")
            self.say_on_speakers(self.finish_phrase)
