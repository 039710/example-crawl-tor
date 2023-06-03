import subprocess
import time
from stem import Signal
from stem.control import Controller

class Tor:
    def __init__(self, tor_control_port):
        self.tor_control_port = tor_control_port
        self.tor_process = None
        self.stop_tor_windows()
        time.sleep(1)
        self.start_tor_windows()
        time.sleep(2)
    def change_ip(self):
        with Controller.from_port(port=self.tor_control_port) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)

    def start_tor_windows(self):
        # Launch Tor process in the background
        subprocess.Popen(["tor"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)        
    def stop_tor_windows(self):
        # Kill Tor process with name tor.exe
        subprocess.Popen("taskkill /F /IM tor.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        

    def start_tor_linux(self):
        # Launch Tor process in the background
        self.tor_process = subprocess.Popen(["tor"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def stop_tor_linux(self):
        self.tor_process.terminate()

    def restart_tor_linux(self):
        self.stop_tor_linux()
        self.start_tor_linux()

    def restart_tor_windows(self):
        self.stop_tor_windows()
        time.sleep(1)
        self.start_tor_windows()
        time.sleep(2)

