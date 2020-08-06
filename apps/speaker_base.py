import appdaemon.plugins.hass.hassapi as hass


class SpeakerBase(hass.Hass):
    def initialize(self):
        self.speakers = self.split_device_list(self.args.get("speakers", "media_player.couch_speaker"))

    def say_on_speakers(self, text):
        self.log(text)
        for speaker in self.speakers: 
            self.call_service('tts/google_say', entity_id=speaker, message=text)
            self.call_service('notify/living_room', message=text)
