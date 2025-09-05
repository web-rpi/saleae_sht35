# SHT35 High-Level Analyzer for Saleae Logic

This high-level analyzer decodes the communication of an **SHT35 temperature and humidity sensor** via **I²C** in Saleae Logic.  

It recognizes:  
- Individual commands  
- Temperature and humidity measurements  
- CRC errors in the measurement data  

---

## Features

- Display of known SHT35 commands  
- Decoding of temperature (°C) and relative humidity (%)  
- CRC checking and marking of faulty measurements  
- Support for I²C addresses in **hexadecimal**  
- Unknown commands are displayed as `Unknown (0xXXXX)`  

---


## Settings

| Setting | Description |
|---------|--------------|
| I2C Address (hex, e.g., 0x44 or 0x45) | Hexadecimal address of the sensor (default: 0x44) |

> **Note:** You can enter the address as either `0x44` or `44`.

---

## Usage

1. Start I²C recording in Saleae Logic.  
2. Add the `SHT35 High-Level Analyzer`.  
3. Select the I²C address of the sensor.  
4. The decoded frames are displayed as follows:

- **Commands**: `CMD: <description>`  
- **Measurements**: `Temp: <°C>, RH: <%>, CRC Error: <True/False>`  

---

## CRC Error

If the data from the sensor is corrupted during transmission, the `crc_error` field is set to `True` and the measurements appear as `None`. This allows for quick detection of communication problems.

---

## Known Commands

- Single shot, high/medium/low repeatability (with/without clock stretching)
- Periodic measurements (0.5–10 measurements per second)  
- Soft reset
- Heater enable/disable
- Read/clear status register

> For a complete list, see `SHT35_COMMANDS` in the code.

---

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute it.
