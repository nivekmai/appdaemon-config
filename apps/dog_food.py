import appdaemon.plugins.hass.hassapi as hass
import datetime
import pprint


class DogFood(hass.Hass):
    def initialize(self):
        self.food_sensor = self.args.get("dog_food", "binary_sensor.dog_food")
        self.fed_sensor = self.args.get("fed_sensor", "binary_sensor.dogs_fed")
        self.speaker = self.args.get("speaker", "media_player.living_room_home")
        self.warning_phrase = self.args.get("warning_phrase", "dogs were already fed")
        self.ack_phrase = self.args.get("acknowledge_phrase", "marking dogs fed")
        self.lunch_reset = self.args.get("lunch_reset", True)
        self.dinner_reset = self.args.get("dinner_reset", True)
        self.set_fed(False)
        self.log("DogFood init: {}".format(pprint.pformat(self.__dict__)))
        self.listen_state(self.on_sensor_change, self.food_sensor)

        bfast_start = datetime.time(5, 0, 0)
        self.run_daily(self.reset_fed, bfast_start)
        if self.lunch_reset:
            lunch_start = datetime.time(11, 0, 0)
            self.run_daily(self.reset_fed, lunch_start)
        if self.dinner_reset:
            dnner_start = datetime.time(15, 0, 0)
            self.run_daily(self.reset_fed, dnner_start)

    def set_fed(self, fed):
        self.fed = fed
        self.set_state(self.fed_sensor, state="on" if fed else "off")

    def say(self, text):
        self.log(text)
        self.call_service("tts/google_say", entity_id=self.speaker, message=text)

    def reset_fed(self, *args):
        self.set_fed(False)

    def is_food_time(self):
        the_hour = datetime.datetime.now().hour
        return 5 <= the_hour <= 22

    def on_sensor_change(self, entity, attribute, old, new, kwargs):
        self.log("INFO: sensor changed ({})".format(new))
        if self.is_food_time():
            if new == "on" and self.fed:
                self.say(self.warning_phrase)
            if new == "off" and not self.fed:
                self.say(self.ack_phrase)
                self.set_fed(True)
