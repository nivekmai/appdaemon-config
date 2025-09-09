import appdaemon.plugins.hass.hassapi as hass
from speaker_base import SpeakerBase


class WasherMonitor(SpeakerBase):
    def initialize(self):
        self.state_sensor = self.args.get("state_sensor", "sensor.washer_state")
        self.power_sensor = self.args.get("power_sensor", "sensor.washer_power")
        self.fill_power_low = float(self.args.get("fill_power_low", "4"))
        self.fill_power_high = float(self.args.get("fill_power_high", "7"))
        self.power_low = float(self.args.get("power_low", "300"))
        self.finish_phrase = self.args.get(
            "finish_phrase", "The washing machine has finished"
        )
        self.power_state = "off"
        self.set_power_state("off")
        self.log("WasherMonitor init: {}".format(self.__dict__))
        self.listen_state(self.on_sensor_change, self.power_sensor)

    def set_power_state(self, state):
        self.power_state = state
        self.set_state(self.state_sensor, state=state)

    def is_filling(self, value):
        return value > self.fill_power_low and value < self.fill_power_high

    def is_spinning(self, value):
        return value > self.power_low

    def on_sensor_change(self, entity, attribute, old, new, kwargs):
        new = float(new)
        if self.power_state == "off":
            if self.is_filling(new):
                self.set_power_state("filling")
        elif self.power_state == "filling":
            if self.is_spinning(new):
                self.set_power_state("washing")
        elif self.power_state == "washing":
            if self.is_filling(new):
                self.set_power_state("refilling")
        elif self.power_state == "refilling":
            if self.is_spinning(new):
                self.set_power_state("rinsing")
        elif new == 0:
            self.set_power_state("off")
            self.say_on_speakers(self.finish_phrase)
