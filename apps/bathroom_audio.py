import appdaemon.plugins.hass.hassapi as hass
import random
from movementlight import MovementLight
from speaker_base import SpeakerBase
import os


class BathroomAudio(MovementLight, SpeakerBase):
    def initialize(self):
        # important! no trailing /
        self.root_dir = self.args.get("root_dir", "/homeassistant/www")
        # important! no trailing /
        self.audio_path = self.args.get("audio_path", "audio")
        # self.log(os.listdir("/config"))

    # Override
    def activate(self):
        self.log("bathroom audio activate")
        (_, _, filenames) = next(os.walk(os.path.join(self.root_dir, self.audio_path)))
        selection = random.randint(0, len(filenames) - 1)
        audio = filenames[selection]
        url = "https://home.nivekmai.com/local/{}/{}".format(self.audio_path, audio)
        for speaker in self.speakers:
            self.log("Playing {} on {}".format(url, speaker))
            self.call_service(
                "media_player/play_media",
                entity_id=speaker,
                media_content_id=url,
                media_content_type="audio/mp3",
            )

    # Override
    def deactivate(self):
        self.log("bathroom audio deactivate")
        for speaker in self.speakers:
            self.call_service("media_player/media_stop", entity_id=speaker)
