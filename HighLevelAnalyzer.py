from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting

I2C_ADDRESS_SETTING = 'I2C Address (hex, e.g., 0x44 or 0x45)'

SHT35_COMMANDS = {
    0x2C06: "Single shot, high repeatability, clock stretching",
    0x2C0D: "Single shot, medium repeatability, clock stretching",
    0x2C10: "Single shot, low repeatability, clock stretching",
    0x2400: "Single shot, high repeatability, no clock stretching",
    0x240B: "Single shot, medium repeatability, no clock stretching",
    0x2416: "Single shot, low repeatability, no clock stretching",
    0x2032: "Periodic measurement, 0.5 mps",
    0x2130: "Periodic measurement, 1 mps",
    0x2236: "Periodic measurement, 2 mps",
    0x2234: "Periodic measurement, 4 mps",
    0x2737: "Periodic measurement, 10 mps",
    0xE000: "Soft reset",
    0x30A2: "Heater enable",
    0x3066: "Heater disable",
    0x3093: "Read status register",
    0x30D3: "Clear status register"
}

def crc8(data):
    crc = 0xFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x31
            else:
                crc <<= 1
            crc &= 0xFF
    return crc

class Hla(HighLevelAnalyzer):
    i2c_address_str = StringSetting(label=I2C_ADDRESS_SETTING)
    
    result_types = {
        'command': {'format': 'CMD: {{data.cmd}}'},
        'measurement': {'format': 'Temp: {{data.temp}}, RH: {{data.rh}}, CRC Error: {{data.crc_error}}'}
    }

    def __init__(self):
        self.buffer = []
        self.current_address = None
        self.start_time = None

    def decode(self, frame: AnalyzerFrame):
        try:
            i2c_address = int(self.i2c_address_str, 16)
        except Exception:
            return None

        if frame.type == 'start':
            self.buffer = []
            self.current_address = None
            self.start_time = frame.start_time

        elif frame.type == 'address':
            self.current_address = frame.data['address'][0]

        elif frame.type == 'data':
            if self.current_address == i2c_address:
                self.buffer.append(frame.data['data'][0])

        elif frame.type == 'stop':
            if self.current_address != i2c_address:
                return None

            end_time = frame.end_time

            if len(self.buffer) == 2:
                cmd = (self.buffer[0] << 8) | self.buffer[1]
                cmd_text = SHT35_COMMANDS.get(cmd, f"Unknown (0x{cmd:04X})")
                return AnalyzerFrame('command', self.start_time, end_time, {'cmd': cmd_text})

            if len(self.buffer) >= 6:
                t_bytes = self.buffer[0:2]
                t_crc = self.buffer[2]
                rh_bytes = self.buffer[3:5]
                rh_crc = self.buffer[5]

                crc_error = (crc8(t_bytes) != t_crc) or (crc8(rh_bytes) != rh_crc)

                raw_t = (t_bytes[0] << 8) | t_bytes[1]
                raw_rh = (rh_bytes[0] << 8) | rh_bytes[1]

                temp = -45 + 175 * raw_t / 65535.0 if not crc_error else None
                rh = 100 * raw_rh / 65535.0 if not crc_error else None

                return AnalyzerFrame('measurement', self.start_time, end_time, {
                    'temp': temp,
                    'rh': rh,
                    'crc_error': crc_error
                })

        return None