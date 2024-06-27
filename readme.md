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
