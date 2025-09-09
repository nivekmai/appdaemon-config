import appdaemon.plugins.hass.hassapi as hass
from speaker_base import SpeakerBase


class NetworkNotify(SpeakerBase):
    def initialize(self):
        self.message = self.args.get("message", "Network has reconnected")
        self.log("init")
        self.listen_event(self.notify, "notify_network_reconnect")

    def notify(self, *args):
        self.say_on_speakers(self.message)
