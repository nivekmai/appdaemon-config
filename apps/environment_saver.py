import appdaemon.plugins.hass.hassapi as hass


class EnvironmentSaver(hass.Hass):
    def initialize(self):
        self.target = self.args["target"]
        self.mode = self.args["mode"]
        self.windows = self.args["windows"]
        self.temperature = self.args["temperature"]
        self.ac = self.args.get("ac", "climate.nest")
        self.speakers = self.split_device_list(self.args.get("speakers", ""))
        self.log(
            "Initializing environment saver: mode: {} target: {} windows: {} temperature: {}".format(
                self.mode, self.target, self.windows, self.temperature
            )
        )
        self.disabling = False
        self.disable_handle = None
        self.listen_state(self.on_target_change, self.target)
        self.listen_state(self.on_mode_change, self.mode)
        self.listen_state(self.on_window_change, self.windows)
        self.listen_state(self.on_temperature_change, self.temperature)
        self.check_should_warn()

    def on_target_change(self, entity, attribute, old, new, kwargs):
        self.log("INFO: target state changed ({})".format(new))
        self.check_should_warn()

    def on_mode_change(self, entity, attribute, old, new, kwargs):
        self.log("INFO: mode state changed ({})".format(new))
        self.check_should_warn()

    def on_temperature_change(self, entity, attribute, old, new, kwargs):
        self.log("INFO: temperature state changed ({})".format(new))
        self.check_should_warn()

    def on_window_change(self, entity, attribute, old, new, kwargs):
        self.log("INFO: window state changed ({})".format(new))
        self.check_should_warn()

    def check_heat(self):
        target = self.get_state(self.target)
        mode = self.get_state(self.mode)
        window = self.get_state(self.windows)
        temperature = self.get_state(self.temperature)
        if mode == "heat" and window == "on" and target >= temperature:
            self.log(
                "INFO: mode: {} and window {} and {} > {}".format(
                    mode, window, target, temperature
                )
            )
            return True
        return False

    def check_cool(self):
        target = self.get_state(self.target)
        mode = self.get_state(self.mode)
        window = self.get_state(self.windows)
        temperature = self.get_state(self.temperature)
        if mode == "cool" and window == "on" and target <= temperature:
            self.log(
                "INFO: mode: {} and window {} and {} < {}".format(
                    mode, window, target, temperature
                )
            )
            return True
        return False

    def say_on_speakers(self, text):
        self.log(text)
        for speaker in self.speakers:
            self.call_service("notify/living_room", message=text)
            self.call_service("tts/google_say", entity_id=speaker, message=text)

    def check_should_warn(self):
        overheating = self.check_heat()
        overcooling = self.check_cool()
        if overheating and not self.disabling:
            self.say_on_speakers(
                "Warning! Heater on and windows open. Close the windows or thermostat will be disabled in 5 minutes."
            )
            self.disabling = True
            self.disable_handle = self.run_in(self.check_should_disable, 300)
            return
        if not overheating and self.disabling:
            self.say_on_speakers("Thank you for doing your part to save the planet")
            self.disabling = False
            self.cancel_timer(self.disable_handle)
            return

        if overcooling and not self.disabling:
            self.say_on_speakers(
                "Warning! Air conditioning on and windows open. Close the windows or thermostat will be disabled in 5 minutes."
            )
            self.disabling = True
            self.run_in(self.check_should_disable, 300)
            return
        if not overcooling and self.disabling:
            self.say_on_speakers("Thank you for doing your part to save the planet")
            self.disabling = False
            self.cancel_timer(self.disable_handle)
            return

    def check_should_disable(self, *args):
        if self.check_cool():
            self.say_on_speakers(
                "We can not cool the planet, turning off the air conditioning."
            )
            self.call_service(
                "climate/set_temperature", entity_id=self.ac, temperature=90
            )
        if self.check_heat():
            self.say_on_speakers("We can not warm the planet, turning off the heater.")
            self.call_service(
                "climate/set_temperature", entity_id=self.ac, temperature=50
            )
        self.disabling = False
