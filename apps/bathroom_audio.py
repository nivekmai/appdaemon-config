import appdaemon.plugins.hass.hassapi as hass
import random
import movementlight as movementlight

MovementLight = movementlight.MovementLight

class BathroomAudio(MovementLight):
    def initialize(self):
        super(BathroomAudio, self).initialize()
        self.speakers = self.split_device_list(self.args.get("speakers", "media_player.hall_bath"))

    def activate(self):
        self.log('bathroom audio activate')
        selection = random.randint(0,64)
        audio = "piano_water{0:03d}.mp3".format(selection)
        url = 'http://www.nivekmai.com/{}'.format(audio)
        for speaker in self.speakers:
            self.log("Playing {} on {}".format(url, speaker))
            self.call_service('media_player/play_media', entity_id=speaker, media_content_id=url, media_content_type='audio/mp3')

    def deactivate(self):
        self.log('bathroom audio deactivate')
        for speaker in self.speakers:
            self.call_service('media_player/media_stop', entity_id=speaker)
