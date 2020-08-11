import appdaemon.plugins.hass.hassapi as hass
from pprint import pformat
from astral import LocationInfo
from astral.sun import elevation
from astral.sun import azimuth
from datetime import time

"""
Controls a cover to open gradually to block the sun based on its elevation.
                _______
                    |        . * < sun
                    |     .
                    |  .
                    | < calculated position of cover to block the sun from being visible by X
                 .  | < additional offset
              .
           .          
        .\\            
     .    \\ <elevation angle
  .        \\
X ----------------------- < 0 degrees
"""


class SunBlinds(hass.Hass):
    def initialize(self):
        # elevation at which blinds should be fully closed (e.g. bottom of the
        # window)
        self.close_elevation = self.args.get("close_elevation")
        # elevation at which blinds should be fully open (e.g. top of the
        # window)
        self.open_elevation = self.args.get("open_elevation")
        # start controling the blinds only if sun is beyond this azimuth
        # (degrees off north)
        self.start_azimuth = self.args.get("start_azimuth", 0)
        # stop controlling blinds once sun has passed this azimuth
        self.end_azimuth = self.args.get("end_azimuth", 360)
        # comma separated list of covers, expected that 0 is fully closed
        # (down) and 100 is fully open
        self.covers = self.split_device_list(self.args["covers"])
        # offset from calculated position of sun added to cover position
        self.offset = self.args.get("offset", 0)
        config = self.get_plugin_config()
        self.locationInfo = LocationInfo(
            "", "", config["time_zone"], config["latitude"], config["longitude"]
        )
        self.log(
            "SunBlinds init: {}".format(
                pformat(
                    {
                        k: v
                        for k, v in self.__dict__.items()
                        if k
                        not in {
                            "_logging",
                            "AD",
                            "config",
                            "app_config",
                            "args",
                            "app_dir",
                            "config_dir",
                            "logger",
                            "err",
                            "lock",
                        }
                    },
                    indent=4,
                )
            )
        )
        self.run_every(self.set_blind_position, "now", 10 * 60)
        self.set_blind_position()

    def set_blind_position(self, *args):
        current_elevation = elevation(self.locationInfo.observer)
        current_azimuth = azimuth(self.locationInfo.observer)
        self.log(
            "current_elevation: {}, open_elevation: {}, close_elevation: {}".format(
                current_elevation, self.open_elevation, self.close_elevation
            )
        )
        self.log(
            "current_azimuth: {}, start_azimuth: {}, end_azimuth: {}".format(
                current_azimuth, self.start_azimuth, self.end_azimuth
            )
        )
        for cover in self.covers:
            if self.start_azimuth <= current_azimuth <= self.end_azimuth:
                position = max(
                    0,
                    min(
                        100,
                        self.offset
                        + (
                            (current_elevation - self.close_elevation)
                            / (self.open_elevation - self.close_elevation)
                            * 100
                        ),
                    ),
                )
                self.log("setting {} to {}".format(cover, position))
                self.call_service(
                    "cover/set_cover_position", entity_id=cover, position=position
                )
            else:
                self.log("not setting blinds, outside azimuth range")
