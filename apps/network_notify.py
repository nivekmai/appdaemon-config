import appdaemon.plugins.hass.hassapi as hass


class NetworkNotify(hass.Hass):
    def initialize(self):
        self.speakers = self.split_device_list(
            self.args.get("speakers", "media_player.living_room_speaker")
        )
        self.message = self.args.get("message", "Network has reconnected")
        self.log("init")
        self.listen_event(self.notify, "notify_network_reconnect")

    def say_on_speakers(self, text):
        self.log(text)
        for speaker in self.speakers:
            self.call_service("tts/google_say", entity_id=speaker, message=text)

    def notify(self, *args):
        self.say_on_speakers(self.message)
