import CleanSweep3D

if __name__ == "__main__":
    ssid = "YOUR_SSID"
    password = "YOUR_PASSWORD"
    printer_IP = "YOUR_PRINTER_IP"
    printer_API = "YOUR_PRINTER_API_KEY"
    prusa_printer = CleanSweep3D.CleanSweep3D(ssid, password, printer_IP, printer_API)
    prusa_printer.run()
