import json
import network
from time import sleep
import view


def load_config():
    with open("config.json") as f:
        return json.load(f)

config = load_config()

class Wlan:
    def __init__(self):
        self.connection = network.WLAN(network.STA_IF)
        self.connection.active(True)
        self.mac = self.connection.config('mac').hex().upper()
        self.ssid = config["wifi"]["ssid"]
        self.password = config["wifi"]["password"]

    def connect(self):
        while not self.connection.isconnected():
            print("Connecting to WiFi...")
            try:
                self.connection.connect(self.ssid, self.password) # start connection to router
                while not self.connection.isconnected():
                    pass
                
            except Exception as e:
                print()
                view.display_center(["WLAN", "CONNECTION", "FAILED","","TRYING AGAIN"])




        print("SELF.IP:", self.connection.ifconfig()[0])



if __name__ == "__main__":
    print(config)

    w = Wlan()
    w.connect()

    print("MAC: ", w.mac)