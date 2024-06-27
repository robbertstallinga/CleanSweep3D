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
- Modified printer parts + scraper arm and servo

## Electrical Connections

### Components
1. **Microcontroller** (e.g., ESP8266, ESP32, etc.)
2. **Servo Motor**
3. **Load Cell with HX711 ADC**
4. **Power Supply** (e.g., 5V or 3.3V depending on the microcontroller and servo motor)

### Pin Connections
1. **Microcontroller to Servo Motor**
    - Servo Signal Pin → GPIO13 (default `servo_gpio` in the code)
    - Servo Power Pin → 5V or 3.3V (depending on your servo motor specifications)
    - Servo Ground Pin → GND

2. **Microcontroller to Load Cell (via HX711)**
    - HX711 `DT` (Data Out) Pin → GPIO16
    - HX711 `SCK` (Clock) Pin → GPIO4
    - HX711 `VCC` Pin → 3.3V or 5V (depending on your HX711 module specifications)
    - HX711 `GND` Pin → GND
    - Load Cell excitation wires (E+ and E-) connect to HX711 E+ and E- respectively.
    - Load Cell signal wires (S+ and S-) connect to HX711 A+ and A- respectively.

### Detailed Diagram

Here's a textual representation of the wiring diagram:

```plaintext
Microcontroller:
+-----------------+
|                 |
|  GPIO13         |-------------> Servo Signal Pin
|  5V/3.3V        |-------------> Servo Power Pin
|  GND            |-------------> Servo Ground Pin
|  GPIO16         |-------------> HX711 DT Pin
|  GPIO4          |-------------> HX711 SCK Pin
|  3.3V/5V        |-------------> HX711 VCC Pin
|  GND            |-------------> HX711 GND Pin
|                 |
+-----------------+

HX711:
+-----------------+
|                 |
|  VCC            |-------------> Microcontroller 3.3V/5V
|  GND            |-------------> Microcontroller GND
|  DT             |-------------> Microcontroller GPIO16
|  SCK            |-------------> Microcontroller GPIO4
|  E+             |-------------> Load Cell E+
|  E-             |-------------> Load Cell E-
|  A+             |-------------> Load Cell S+
|  A-             |-------------> Load Cell S-
|                 |
+-----------------+

