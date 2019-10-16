import appdaemon.plugins.hass.hassapi as hass
import json
from datetime import datetime, time, date, timedelta


class LightFlux(hass.Hass):
    
    def initialize(self):
        self.start_str = self.args.get('start', '20:30:00')
        self.finish_str = self.args.get('finish', '23:55:00')
        self.start_level = int(self.args.get('start_level', '255'))
        self.finish_level = int(self.args.get('finish_level', '10'))
        self.reset_time_str = self.args.get('reset_time', '07:00:00')
        self.toggle = self.args.get("toggle", "input_boolean.auto_dimmer")
        self.lights = self.split_device_list(
            self.args.get('levels', "light.laundry_light_level,"
                                    "light.dining_level,"
                                    "light.kitchen_level,"
                                    "light.couch_level,"
                                    "light.entry_light,"
                                    "light.hall_bath_level,"
                                    "light.master_bath_main_level,"
                                    "light.master_bath_mirr_level,"
                                    "light.master_hall_level,"
                                    "light.guest_bath_level,"
                                    "light.guest_level,"
                                    "light.office_level"))
        self.handlers = {}
        self.level = self.start_level
        self.log('LightFlux init: {}'.format(json.dumps(
            {
                "start": self.start_str,
                "finish": self.finish_str,
                "reset_time": self.reset_time_str,
                "start_level": self.start_level,
                "finish_level": self.finish_level,
                "lights": self.lights,
            }, indent=2)))

        # Setup listeners
        self.parse_times()
        self.setup_timers()

    def parse_times(self, *args):
        self.start = datetime.combine(date.today(), self.parse_time(self.start_str))
        self.finish = datetime.combine(date.today(), self.parse_time(self.finish_str))
        self.reset_time = datetime.combine(date.today(), self.parse_time(self.reset_time_str))
        self.time_delta = self.finish - self.start

    def setup_timers(self):
        self.run_daily(self.parse_times, time(0,0,1))
        self.run_minutely(self.on_schedule, time(0,0,0))
        
    def should_operate(self):
        if (datetime.now() < self.start):
            self.log("not running, too early")
            return False
        elif (self.get_state(self.toggle) != "on"):
            self.log("not running, boolean off")
            return False
        return True
        
    def calculate_dim(self):
        delta_from_start = datetime.now() - self.start
        level = self.start_level - int(delta_from_start.total_seconds() / self.time_delta.total_seconds() * self.start_level) + self.finish_level
        self.log("calculated dim: {}".format(level))
        return max(level, self.finish_level)

    def on_schedule(self, *args):
        reset = False
        if self.reset_time < datetime.now() and datetime.now() < self.reset_time + timedelta(minutes=1):
            self.level = self.start_level
            reset = True
            self.turn_on(self.toggle)
        elif self.should_operate():
            self.level = self.calculate_dim()
        else:
            return
        offset = 0
        for light in self.lights:
            light = light.strip()
            self.run_in(self.set_dim, offset, light=light, reset=reset)
            offset += 2 # allow 1 second for reset

    def set_dim(self, *args):
        '''Set the dim level, if the light is off, set up a handler'''
        self.log("set_dim: {}".format(args[0]))
        light = args[0].get('light')
        reset = args[0].get('reset')
        current_setting = self.get_state(light)
        current_brightness = self.get_state(light, attribute="brightness")
        self.log('setting {} to {}, state: {}, level: {}'.format(light, self.level, current_setting, current_brightness))
        if current_setting == 'on':
            self.turn_on(light, brightness=self.level)
        elif reset == True:
            self.turn_on(light, brightness=self.level)
            self.run_in(self.turn_back_off, 1, light=light)
        else:
            handler = self.handlers.get(light)
            if handler is not None:
                self.cancel_listen_state(handler)
            self.handlers[light] = self.listen_state(self.handle_dim, light, new='on')

    def handle_dim(self, light, attr, old, new, kwargs):
        self.log('handle_dim light: {}, level: {}'.format(light, self.level))
        self.cancel_listen_state(self.handlers[light])
        self.turn_on(light, brightness=self.level)

    def turn_back_off(self, *args):
        light = args[0].get('light')
        self.log('turning {} back off'.format(light))
        self.turn_off(light)

