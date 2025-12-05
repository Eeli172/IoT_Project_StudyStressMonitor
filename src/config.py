import json
import network
import ntptime
import time



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
        self.timestamp = None


    def connect(self): # method to connect to wlan
        print("Connecting to WiFi...")
        try:
            self.connection.connect(self.ssid, self.password) # start connection to router
            while not self.connection.isconnected(): # wait until connection is up
                pass
            
        except Exception as e: # in case something goes wrong
            print("exception occurred while connecting to wlan:".upper(), e)
            # import view here to avoid a circular import at module level                
            raise Exception("Failed connecting to wlan")

        # print ip when connected
        print("SELF.IP:", self.connection.ifconfig()[0])
        
        # synchronize time
        self.sync_time()


    def sync_time(self):
        ntptime.host = "fi.pool.ntp.org"
        ntptime.settime()   # now the Pico's RTC is in UTC
        


    def get_time(self):
        timestamp = time.time()         # timestamp
        timezone = 2 * 3600             # UTC +2 timezone difference
        self.timestamp = timestamp + timezone 

        

    def format_time(self, timestamp):
        t = time.localtime(timestamp)
    
        long = "{:02d}.{:02d}.{:04d} {:02d}.{:02d}".format(
            t[2], t[1], t[0], t[3], t[4]
        )
        
        short = "{:02d}.{:02d}. {:02d}.{:02d}".format(
            t[2], t[1], t[3], t[4]
        )
        
        return long, short



if __name__ == "__main__": # main block for testing
    w = Wlan()
    print("   timestamp before sync:",time.time())
    w.connect()
    print("   timestamp after sync:",time.time())