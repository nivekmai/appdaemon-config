import appdaemon.plugins.hass.hassapi as hass
import json


class TeslaCheck(hass.Hass):
    def initialize(self):
        check_times = self.split_device_list(
            self.args.get('check_times', '22:00:00'))
        self.charge_sensor = self.args.get(
            'charge_sensor',
            'binary_sensor.tesla_model_s_5yjsa1h20ffp78391_charger_sensor')
        self.battery_sensor = self.args.get(
            'battery_sensor',
            'sensor.tesla_model_s_5yjsa1h20ffp78391_battery_sensor')
        self.speakers = self.split_device_list(self.args.get(
            "speakers", "media_player.living_room_home,media_player.office,media_player.couch_speaker,media_player.master_bedroom_home"))
        self.charge_level = int(self.args.get(
            'charge_level',
            50))
        self.car_name = self.args.get('name', 'Model S')
        self.log('Tesla check init: {}'.format(json.dumps(
            {
                "check_times": check_times,
                "charge_sensor": self.charge_sensor,
                "battery_sensor": self.battery_sensor,
                "speakers": self.speakers,
                "charge_level": self.charge_level,
            }, indent=2)))

        # Setup listeners
        self.listen_event(self.check_charging, "CHECK_CHARGE")
        for check_time in check_times:
            time = self.parse_time(check_time.strip())
            self.run_daily(self.check_charging, time)

    def say_on_speakers(self, text):
        self.log(text)
        for speaker in self.speakers:
            self.call_service(
                'tts/google_say', entity_id=speaker, message=text)

    def check_charging(self, *args):
        charge_state = self.get_state(self.charge_sensor)
        battery_level = int(self.get_state(self.battery_sensor))
        charge_level = self.charge_level
        if(charge_state == 'off' and battery_level <= charge_level):
            self.say_on_speakers('{} needs to be plugged in'.format(self.car_name))
        else:
            self.log(
                "charge level {}, charge_state {}, battery_level {}".format(
                    charge_level, charge_state, battery_level))
