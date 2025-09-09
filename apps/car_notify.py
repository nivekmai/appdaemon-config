import speaker_base as speaker_base

SpeakerBase = speaker_base.SpeakerBase


class CarNotify(SpeakerBase):
    def initialize(self):
        super().initialize()
        self.say_on_speakers("hello")
