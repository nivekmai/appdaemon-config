import appdaemon.plugins.hass.hassapi as hass


class SensorCommand(hass.Hass):
    '''Fires off an IR command when a sensor is tripped'''
    def initialize(self):
        self.sensor = self.args.get('sensor', 'binary_sensor.hall_bath_door_handle')
        self.packet = self.args.get('package', 'JgD8AMJjEhISNxMSERMSEhIUERMRExETEhMSEhI3EhMRExISEhMSExETERMSExISEhMRExM2EjcROBE3ExISNxE4EhIUNhE3EjcSNxETEjcSNxITEgAD9MNjERMRNxMSEhMRExEUERMSEhITERQRExE3ExISExETERMSExISEhMRFBETERMSEhI4ETcSNxI3EhMRNxI4ERMROBI3ETgRNxITEjcRNxMSEgAD9cNiERMSNxITERMRExITEhISExETEhMRExI3EhMRExETEhMSEhITERMRFBETEhISExE4ETcTNxE3EhMSNxE4ERMSNxM1EjYUNxETFDUSNxITEQANBQAAAAAAAAAAAAAAAA')
        self.ir_service = self.args.get('ir_service', 'switch/broadlink_send_packet_192_168_1_151')
        self.log("Initializing sensor command: sensor {} packet: {} IR service: {}"
                 .format(self.sensor, self.packet, self.ir_service))
        self.listen_state(self.on_sensor_change, self.sensor)


    def on_sensor_change(self, entity, attribute, old, new, kwargs):
        self.log("INFO: sensor state changed ({})".format(new))
        if (new == "on"):
            self.log("INFO: firing packet")
            self.call_service(self.ir_service, packet = self.packet)
