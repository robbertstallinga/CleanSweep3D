# CleanSweep3D

CleanSweep3D is a microPython class designed to interact with Prusa 3D printers using a Wi-Fi connection. This project provides functionalities to monitor and control the printer states, including connecting to Wi-Fi, handling print jobs, and managing a simple web server to display the printer status.

## Features

- Connect to a Wi-Fi network.
- Retrieve printer information and status.
- Control a servo motor to assist in print removal.
- Simple web server to display the printer state.
- State machine to handle different printer states: Connecting, Idle, Printing, and Removing.

## Installation

### Prerequisites

- Thonny or similar IDE for hardware control (microPython)
- Prusa MK3.9/MK4 with network capabilities
- ESP32 with microPython
- WiFi network
- Working Load cell using the HX711
- Servo motor
- Buck converter 
- Modified printer parts + scraper arm and servo

## Electrical Connections

### Components
1. **Microcontroller** (e.g., ESP8266, ESP32, etc.)
2. **Servo Motor**
3. **Load Cell with HX711 ADC**
4. **Buck Converter** (to step down 24V to 5V)
5. **Power Supply** (24V from Prusa 3D printer)

### Pin Connections
1. **Prusa 24V to Buck Converter**
    - 24V Input → Prusa 24V Output
    - GND → Prusa GND
    - 5V Output → Components (Microcontroller, Servo Motor, HX711)

2. **Microcontroller to Servo Motor**
    - Servo Signal Pin → GPIO13 (default `servo_gpio` in the code)
    - Servo Power Pin → 5V from Buck Converter
    - Servo Ground Pin → GND from Buck Converter

3. **Microcontroller to Load Cell (via HX711)**
    - HX711 `DT` (Data Out) Pin → GPIO16
    - HX711 `SCK` (Clock) Pin → GPIO4
    - HX711 `VCC` Pin → 5V from Buck Converter
    - HX711 `GND` Pin → GND from Buck Converter
    - Load Cell excitation wires (E+ and E-) connect to HX711 E+ and E- respectively.
    - Load Cell signal wires (S+ and S-) connect to HX711 A+ and A- respectively.

### Detailed Diagram

Here's a textual representation of the wiring diagram:

```plaintext
Prusa 3D Printer:
+---------------------+
|                     |
|  24V Output         |-------------> Buck Converter 24V Input
|  GND                |-------------> Buck Converter GND
|                     |
+---------------------+

Buck Converter:
+---------------------+
|                     |
|  24V Input          |-------------> Prusa 24V Output
|  GND                |-------------> Prusa GND
|  5V Output          |-------------> Components 5V Input
|  GND                |-------------> Components GND
|                     |
+---------------------+

Microcontroller:
+---------------------+
|                     |
|  GPIO13             |-------------> Servo Signal Pin
|  5V                 |-------------> Buck Converter 5V Output
|  GND                |-------------> Buck Converter GND
|  GPIO16             |-------------> HX711 DT Pin
|  GPIO4              |-------------> HX711 SCK Pin
|                     |
+---------------------+

Servo:
+---------------------+
|                     |
|  5V Input           |-------------> Buck converter 5V output
|  GND                |-------------> Buck converter GND
|  PWM pin            |-------------> ESP32 GPIO13
|                     |
+---------------------+

HX711:
+---------------------+
|                     |
|  VCC                |-------------> ESP32 3V3 output
|  GND                |-------------> ESP23 GND
|  DT                 |-------------> Microcontroller GPIO16
|  SCK                |-------------> Microcontroller GPIO4
|  E+                 |-------------> Load Cell E+
|  E-                 |-------------> Load Cell E-
|  A+                 |-------------> Load Cell S+
|  A-                 |-------------> Load Cell S-
|                     |
+---------------------+

