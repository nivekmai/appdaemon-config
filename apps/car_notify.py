from speaker_base import SpeakerBase


class CarNotify(SpeakerBase):
    def initialize(self):
        self.say_on_speakers("hello")
