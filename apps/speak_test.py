import appdaemon.plugins.hass.hassapi as hass
from speaker_base import SpeakerBase

class SpeakTest(SpeakerBase):
    def initialize(self):
        self.say_on_speakers("hello")