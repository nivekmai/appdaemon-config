import appdaemon.plugins.hass.hassapi as hass
import datetime
import json
from speaker_base import SpeakerBase


class PresenceLock(SpeakerBase):
    def initialize(self):
        self.presence = self.args.get(
            "presence",
            "device_tracker." "tesla_model_s_5yjsa1h20ffp78391" "_location_tracker",
        )
        self.lock = self.args.get("lock", "lock.front_door_lock")
        self.arrival_phrase = self.args.get("arrival_phrase", "Kevin is home")
        self.log(
            "init: {}".format(
                json.dumps(
                    {
                        "presence": self.presence,
                        "lock": self.lock,
                        "speaker": self.speaker,
                        "arrival_phrase": self.arrival_phrase,
                    },
                    indent=4,
                )
            )
        )
        self.listen_state(self.on_presence_change, self.presence)

    def on_presence_change(self, entity, attribute, old, new, kwargs):
        self.log("INFO: sensor changed ({}) -> ({})".format(old, new))
        if new == "home" and old == "away":
            self.call_service("lock/unlock", entity_id=self.lock)
            self.say_on_speakers(self.arrival_phrase)
        if new == "away" and old == "home":
            self.call_service("lock/lock", entity_id=self.lock)
