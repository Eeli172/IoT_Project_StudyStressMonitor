import json
import network
import view



def load_config(): # get config from config.json
    with open("config.json") as f:
        return json.load(f)

config = load_config() # config to import



class Wlan: # wlan class
    def __init__(self):
        self.connection = network.WLAN(network.STA_IF)
        self.connection.active(True)
        self.mac = self.connection.config('mac').hex().upper()
        self.ssid = config["wifi"]["ssid"]
        self.password = config["wifi"]["password"]


    def connect(self): # method to connect to wlan
        while not self.connection.isconnected(): # try until connection establsihed
            print("Connecting to WiFi...")
            try:
                self.connection.connect(self.ssid, self.password) # start connection to router
                while not self.connection.isconnected(): # wait until connection is up
                    pass
                
            except Exception as e: # in case something goes wrong
                print("exception occurred while connecting to wlan:".upper(), e)
                view.display_center(["WLAN", "CONNECTION", "FAILED","","TRYING AGAIN"])

        # print ip when connected
        print("SELF.IP:", self.connection.ifconfig()[0])



if __name__ == "__main__": # main block for testing
    print(config)

    w = Wlan()
    w.connect()

    print("MAC: ", w.mac)