import appdaemon.plugins.hass.hassapi as hass
import pprint
import datetime

"""
Hue analog clock. Rotates through 360 degrees of hue every 12 hours, showing
as if an analog clock's hour hand positioned on the circumference of a color 
wheel is used to configure the RGB values
"""
class RgbClock(hass.Hass):
    def initialize(self):
        # Lights, defined as a comma separated list of time_strings
        self.light = self.args.get("light")
        pp = pprint.PrettyPrinter(depth=4)
        self.log("RgbClock init: {}".format(pp.pformat(self.__dict__["args"])))
        time = datetime.time(0, 0, 0)
        self.run_minutely(self.on_minute, time)


    def on_minute(self, kwargs):
        time = datetime.datetime.now()
        hour = (time.hour - 12) if time.hour > 12 else time.hour
        minute = time.minute
        # hour = 8
        # minute = 30
        val = ((hour * 60) + minute) / 2
        if minute == 0:
            for i in range(0, hour):
                self.run_in(self.go_off, 2*i)
                self.run_in(self.go_white, 2*i+1)
            self.run_in(self.go_off, 2*hour)
            self.run_in(self.go_color, 2*hour+1, val=val)
        if minute == 30:
            self.run_in(self.go_off, 0)
            self.run_in(self.go_color, 3, val=val)
        else:
            self.run_in(self.go_color, 0, val=val)
        self.log('The time is {:%H:%M}. The value is {}'.format(time, val))
        
    def go_color(self, kwargs):
        self.call_service("light/turn_on", entity_id = self.light, hs_color = [kwargs["val"], 100])
        
    def go_white(self, kwargs):
        self.call_service("light/turn_on", entity_id = self.light, color_name="white")
        
    def go_off(self, kwargs):
        self.call_service("light/turn_off", entity_id = self.light)
