import appdaemon.plugins.hass.hassapi as hass


class SpeakTest(hass.Hass):
    def initialize(self):
        self.call_service("light/turn_off", entity_id = "light.couch")
        self.log("hello")
        self.call_service(
                "tts/google_translate_say", entity_id="media_player.couch_speaker", message="hello"
            )