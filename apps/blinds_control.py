import appdaemon.plugins.hass.hassapi as hass

class BlindsControl(hass.Hass):
    def initialize(self):
        # Times, defined as a comma separated list of time_string s
        on_times = self.split_device_list(self.args["open_times"])
        off_times = self.split_device_list(self.args["close_times"])
        # Switches, defined as a comma separated list
        self.windows = self.split_device_list(self.args["windows"])
        self.speakers = self.split_device_list(self.args.get("speakers", ""))
        self.open_scene = self.args.get("open_scene")
        self.close_scene = self.args.get("close_scene")
        self.listen_handler = None
        self.log('Blind control init: {}'.format(self.__dict__))
        self.listen_event(self.close_blinds, "TRIGGER_BLIND_CLOSE")
        self.listen_event(self.open_blinds, "TRIGGER_BLIND_OPEN")

        for on_time in on_times:
            time = self.parse_time(on_time)
            self.run_daily(self.open_blinds, time)
        for off_time in off_times:
            time = self.parse_time(off_time)
            self.run_daily(self.close_blinds, time)

    def say_on_speakers(self, text):
        self.log(text)
        for speaker in self.speakers:
            self.call_service('tts/google_say', entity_id=speaker, message=text)

    def open_blinds(self, *args):
        self.say_on_speakers('Opening blinds')
        self.call_service('scene/turn_on',
                          entity_id=self.open_scene)
        self.cancel_listen()

    def close_blinds(self, *args):
        ok_to_close = True
        for window in self.windows:
            self.log('window {} state: {}'.format(window, self.get_state(window)))
            if self.get_state(window) == 'on':
                self.log(
                        'Refusing to close blinds, {} is still open'
                        .format(self.friendly_name(window)))
                self.listen_handler = self.listen_state(self.close_blinds, window, new='off')
                self.log('listening for changes to {}'.format(window))
                ok_to_close = False
                break
        if ok_to_close:
            self.call_service('scene/turn_on',
                              entity_id=self.close_scene)
            self.say_on_speakers('Closing the blinds')
            self.cancel_listen()

    def cancel_listen(self):
        self.log('cancelling listener')
        self.cancel_listen_event(self.listen_handler)
