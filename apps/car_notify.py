import speaker_base as speaker_base
SpeakerBase = speaker_base.SpeakerBase

class CarNotify(SpeakerBase):
    def initialize(self):
        super().initialize()
	self.car = self.args.get()
