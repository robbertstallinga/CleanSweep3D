import network
from time import sleep
import machine
import urequests
import socket
import _thread
from utime import sleep_us, time
from machine import Pin
from micropython import const


class CleanSweep3D:
    """
    CleanSweep3D class to interact with Prusa 3D printers.
    """

    def __init__(self, ssid: str, password: str, ip: str, api_key: str, port=80, servo_gpio=13) -> None:
        """
        Initialize Prusalink class
        Args:
            ssid (str): WiFi SSID
            password (str): WiFi Password
            ip (str): Printer IP address
            api_key (str): API key for accessing the printer
            port (int): Port number (default is 80)
            servo_gpio (int): GPIO pin for the servo (default is 13)
        """
        self.ssid = ssid
        self.password = password
        self.ip = ip
        self.port = str(port)
        self.api_key = api_key
        self.headers = {'X-Api-Key': api_key}
        self.servo_gpio = servo_gpio

        # Define states for the printer interaction
        self.STATE_CONNECTING = 0
        self.STATE_IDLE = 1
        self.STATE_PRINTING = 2
        self.STATE_REMOVING = 3

        # Initialize the servo motor
        self.servo_pin = machine.Pin(servo_gpio)
        self.servo = machine.PWM(self.servo_pin, freq=50)
        self.arm_up = 140
        self.arm_down = 0

        # Define sleep intervals for different states
        self.idle_sleep = 5.0
        self.printing_sleep = 1.0
        self.removing_sleep = 0.5
        self.current_state = self.STATE_CONNECTING
        self.error_message = ""

        # # Initialize load cell, commented out for testing
        # self.lc = Scales(d_out=16, pd_sck=4)
        # self.lc.reset()
        # self.lc.tare()
        self.weight = 50
        print(f"Sensor weight: {self.weight}")
        self.collected_prints = 0

    def get_printer_info(self):
        """
        Get the current state and information of the printer.
        Returns:
            dict: Printer information if successful, None otherwise
        """
        url = f"http://{self.ip}/api/printer"
        headers = {
            "X-Api-Key": self.api_key
        }
        try:
            response = urequests.get(url, headers=headers)
            if response.status_code == 200:
                self.error_message = ""  # Clear error message on success
                return response.json()
            else:
                self.error_message = f"HTTP Error: {response.status_code}\nResponse content: {response.text}"
                self.post_error()
                return None
        except ValueError as ve:
            self.error_message = f"JSON decoding failed: {ve}\nResponse content: {response.text}"
            self.post_error()
            return None
        except Exception as e:
            self.error_message = f"Failed to get printer info: {e}"
            self.post_error()
            return None

    def do_connect(self):
        """
        Connect to the Wi-Fi network.
        Returns:
            bool: True if connected successfully, False otherwise
        """
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
            print('connecting to network...')
            sta_if.active(True)
            sta_if.connect(self.ssid, self.password)

            max_wait = 10  # Timeout after 10 seconds
            while not sta_if.isconnected() and max_wait > 0:
                print('waiting for connection...')
                sleep(1)
                max_wait -= 1

        if sta_if.isconnected():
            print('network config:', sta_if.ifconfig())
            print('Connected to Wi-Fi!')
            # Start the server in a separate thread
            _thread.start_new_thread(self.start_server, ())
            return True
        else:
            print('Failed to connect to Wi-Fi.')
            return False

    def set_servo_angle(self, start_angle, end_angle, step=1, delay=0.02):
        """
        Move the servo to the specified angle.
        Args:
            start_angle (int): Starting angle
            end_angle (int): Ending angle
            step (int): Step size for angle increment (default is 1)
            delay (float): Delay between steps in seconds (default is 0.02)
        """
        min_duty = 40
        max_duty = 115

        # Determine the direction of the step (positive or negative)
        if start_angle < end_angle:
            angle_range = range(start_angle, end_angle + 1, step)
        else:
            angle_range = range(start_angle, end_angle - 1, -step)

        for angle in angle_range:
            duty = min_duty + (max_duty - min_duty) * (angle / 180)
            self.servo.duty(int(duty))
            sleep(delay)

    def state_connecting(self):
        """
        Handle the connecting state. Attempt to connect to Wi-Fi and
        initialize the servo position if successful.
        """
        if self.do_connect():
            self.set_servo_angle(self.arm_up, self.arm_down)
            sleep(3.0)
            self.set_servo_angle(self.arm_down, self.arm_up)
            self.current_state = self.STATE_IDLE
        else:
            sleep(5)  # Retry after 5 seconds

    def state_idle(self):
        """
        Handle the idle state. Check the printer status and update state
        accordingly.
        """
        printer_info = self.get_printer_info()
        if printer_info:
            status = printer_info["state"]["flags"]["printing"]
            self.set_servo_angle(self.arm_up, self.arm_up)
            if status:
                self.current_state = self.STATE_PRINTING
                print("Printing")
            else:
                print("Not printing")
        else:
            print("Failed to retrieve printer info")
        sleep(self.idle_sleep)

    def state_printing(self):
        """
        Handle the printing state. Monitor the nozzle temperature to determine
        if the print is complete.
        """
        printer_info = self.get_printer_info()
        if printer_info:
            nozzle_target = printer_info["temperature"]["tool0"]["target"]
            print(f"Nozzle target: {nozzle_target}")
            self.set_servo_angle(self.arm_up, self.arm_up)
            if nozzle_target == 28:  # Flag to indicate removing can be started
                self.set_servo_angle(self.arm_up, self.arm_down)
                self.current_state = self.STATE_REMOVING
            status = printer_info["state"]["flags"]["printing"]
            if not status:
                self.set_servo_angle(self.arm_up, self.arm_up)
                self.current_state = self.STATE_IDLE
        else:
            print("Failed to retrieve printer info")
        sleep(self.printing_sleep)

    def state_removing(self):
        """
        Handle the removing state. Control the servo to assist in print
        removal and return to idle state.
        """
        print("Removing print")
        printer_info = self.get_printer_info()
        if printer_info:
            self.set_servo_angle(self.arm_down, self.arm_down)
            nozzle_target = printer_info["temperature"]["tool0"]["target"]
            print(f"Nozzle target: {nozzle_target}")
            if nozzle_target == 29:  # Flag to indicate removing is done
                self.set_servo_angle(self.arm_down, self.arm_up)
                sleep(1.0)
                temp_weight = self.weight + 150
                weight_diff = temp_weight - self.weight
                print(f"Weight difference: {weight_diff}")
                if weight_diff > 100:
                    self.collected_prints = self.collected_prints + 1
                    print(f"Print removed, total: {self.collected_prints}")
                    self.weight = temp_weight
                    self.post_collected_prints()
                    self.current_state = self.STATE_IDLE
                else:
                    print("Collecting print error")
                    self.error_message = "Print not collected, check printer"
                    self.post_error()
                    self.post_collected_prints()
                    self.current_state = self.STATE_IDLE
        else:
            print("Failed to retrieve printer info")
        sleep(self.removing_sleep)

    def start_server(self):
        """
        Start a simple web server to serve the printer state.
        """
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        s = socket.socket()
        s.bind(addr)
        s.listen(1)
        print('Listening on', addr)

        while True:
            cl, addr = s.accept()
            print('Client connected from', addr)
            request = cl.recv(1024).decode('utf-8')
            print('Request:', request)
            state = 'Connecting' if self.current_state == self.STATE_CONNECTING else \
                'Idle' if self.current_state == self.STATE_IDLE else \
                    'Printing' if self.current_state == self.STATE_PRINTING else \
                    'Removing'
            response = f"""
            <html>
            <head>
                <title>CleanSweep 3D status</title>
            </head>
            <body>
                <h1>CleanSweep 3D status</h1>
                <p>Current State: {state}</p>
                <p>Error: {self.error_message}</p>
                <p>Collected Prints: {self.collected_prints}</p>
            </body>
            </html>
            """
            cl.send('HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(response)
            cl.close()

    def post_state(self):
        """
        Method to post the current state to the web server.
        """
        state = 'Connecting' if self.current_state == self.STATE_CONNECTING else \
            'Idle' if self.current_state == self.STATE_IDLE else \
                'Printing' if self.current_state == self.STATE_PRINTING else \
                'Removing'
        return state

    def post_error(self):
        """
        Method to post the current error message to the web server.
        """
        return self.error_message

    def post_collected_prints(self):
        """
        Method to post the number of collected prints to the web server.
        """
        return self.collected_prints

    def run(self):
        """
        Main loop to run the state machine. Transition between states based
        on the current state.
        """
        while True:
            if self.current_state == self.STATE_CONNECTING:
                self.state_connecting()
                print(f"Current state: {self.current_state}")
            elif self.current_state == self.STATE_IDLE:
                self.state_idle()
                print(f"Current state: {self.current_state}")
            elif self.current_state == self.STATE_PRINTING:
                self.state_printing()
                print(f"Current state: {self.current_state}")
            elif self.current_state == self.STATE_REMOVING:
                self.state_removing()
                print(f"Current state: {self.current_state}")


class HX711Exception(Exception):
    pass


class InvalidMode(HX711Exception):
    pass


class DeviceIsNotReady(HX711Exception):
    pass


class HX711(object):
    """
    Micropython driver for Avia Semiconductor's HX711
    24-Bit Analog-to-Digital Converter
    """
    CHANNEL_A_128 = const(1)
    CHANNEL_A_64 = const(3)
    CHANNEL_B_32 = const(2)

    DATA_BITS = const(24)
    MAX_VALUE = const(0x7fffff)
    MIN_VALUE = const(0x800000)
    READY_TIMEOUT_SEC = const(5)
    SLEEP_DELAY_USEC = const(80)

    def __init__(self, d_out: int, pd_sck: int, channel: int = CHANNEL_A_128):
        self.d_out_pin = Pin(d_out, Pin.IN)
        self.pd_sck_pin = Pin(pd_sck, Pin.OUT, value=0)
        self.channel = channel

    def __repr__(self):
        return "HX711 on channel %s, gain=%s" % self.channel

    def _convert_from_twos_complement(self, value: int) -> int:
        """
        Converts a given integer from the two's complement format.
        """
        if value & (1 << (self.DATA_BITS - 1)):
            value -= 1 << self.DATA_BITS
        return value

    def _set_channel(self):
        """
        Input and gain selection is controlled by the
        number of the input PD_SCK pulses
        3 pulses for Channel A with gain 64
        2 pulses for Channel B with gain 32
        1 pulse for Channel A with gain 128
        """
        for i in range(self._channel):
            self.pd_sck_pin.value(1)
            self.pd_sck_pin.value(0)

    def _wait(self):
        """
        If the HX711 is not ready within READY_TIMEOUT_SEC
        the DeviceIsNotReady exception will be thrown.
        """
        t0 = time()
        while not self.is_ready():
            if time() - t0 > self.READY_TIMEOUT_SEC:
                raise DeviceIsNotReady()

    @property
    def channel(self) -> tuple:
        """
        Get current input channel in a form
        of a tuple (Channel, Gain)
        """
        if self._channel == self.CHANNEL_A_128:
            return 'A', 128
        if self._channel == self.CHANNEL_A_64:
            return 'A', 64
        if self._channel == self.CHANNEL_B_32:
            return 'B', 32

    @channel.setter
    def channel(self, value):
        """
        Set input channel
        HX711.CHANNEL_A_128 - Channel A with gain 128
        HX711.CHANNEL_A_64 - Channel A with gain 64
        HX711.CHANNEL_B_32 - Channel B with gain 32
        """
        if value not in (self.CHANNEL_A_128, self.CHANNEL_A_64, self.CHANNEL_B_32):
            raise InvalidMode('Gain should be one of HX711.CHANNEL_A_128, HX711.CHANNEL_A_64, HX711.CHANNEL_B_32')
        else:
            self._channel = value

        if not self.is_ready():
            self._wait()

        for i in range(self.DATA_BITS):
            self.pd_sck_pin.value(1)
            self.pd_sck_pin.value(0)

        self._set_channel()

    def is_ready(self) -> bool:
        """
        When output data is not ready for retrieval,
        digital output pin DOUT is high.
        """
        return self.d_out_pin.value() == 0

    def power_off(self):
        """
        When PD_SCK pin changes from low to high
        and stays at high for longer than 60 us ,
        HX711 enters power down mode.
        """
        self.pd_sck_pin.value(0)
        self.pd_sck_pin.value(1)
        sleep_us(self.SLEEP_DELAY_USEC)

    def power_on(self):
        """
        When PD_SCK returns to low, HX711 will reset
        and enter normal operation mode.
        """
        self.pd_sck_pin.value(0)
        self.channel = self._channel

    def read(self, raw=False):
        """
        Read current value for current channel with current gain.
        if raw is True, the HX711 output will not be converted
        from two's complement format.
        """
        if not self.is_ready():
            self._wait()

        raw_data = 0
        for i in range(self.DATA_BITS):
            self.pd_sck_pin.value(1)
            self.pd_sck_pin.value(0)
            raw_data = raw_data << 1 | self.d_out_pin.value()
        self._set_channel()

        if raw:
            return raw_data
        else:
            return self._convert_from_twos_complement(raw_data)


class Scales(HX711):
    def __init__(self, d_out, pd_sck):
        super(Scales, self).__init__(d_out, pd_sck)
        self.offset = 0

    def reset(self):
        self.power_off()
        self.power_on()

    def tare(self):
        self.offset = self.read()

    def raw_value(self):
        return self.read() - self.offset

    def stable_value(self, reads=10, delay_us=500):
        values = []
        for _ in range(reads):
            values.append(self.raw_value())
            sleep_us(delay_us)
        return self._stabilizer(values)

    @staticmethod
    def _stabilizer(values, deviation=10):
        weights = []
        for prev in values:
            if prev == 0:
                continue  # Skip zero values to avoid division by zero
            weights.append(sum([1 for current in values if abs(prev - current) / (prev / 100) <= deviation]))
        if not weights:  # If all values were zero, return zero
            return 0
        return sorted(zip(values, weights), key=lambda x: x[1]).pop()[0]
