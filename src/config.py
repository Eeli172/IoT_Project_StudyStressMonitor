import json
import network
import ntptime
import machine
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
        self.time = None


    def connect(self): # method to connect to wlan
        while not self.connection.isconnected(): # try until connection establsihed
            print("Connecting to WiFi...")
            try:
                self.connection.connect(self.ssid, self.password) # start connection to router
                while not self.connection.isconnected(): # wait until connection is up
                    pass
                
            except Exception as e: # in case something goes wrong
                print("exception occurred while connecting to wlan:".upper(), e)
                # import view here to avoid a circular import at module level                
                import view
                view.display_center(["WLAN", "CONNECTION", "FAILED","","TRYING AGAIN"])

        # print ip when connected
        print("SELF.IP:", self.connection.ifconfig()[0])
        
        # synchronize time
        self.sync_time()


    def sync_time(self):
        timezone_offset = 2*3600 # UTC+2
        ntptime.host = "fi.pool.ntp.org"
        ntptime.settime()   # now the Pico's RTC is in UTC

        rtc = machine.RTC()
        utc = time.time()
        local = time.localtime(utc + timezone_offset)

        rtc.datetime((
            local[0],  # year
            local[1],  # month
            local[2],  # day
            local[6],  # weekday (0 = Monday)
            local[3],  # hours
            local[4],  # minutes
            local[5],  # seconds
            0          # subseconds
        ))

    def get_time(self):
        _time = time.localtime() # returns long format "DD.MM.YYYY hh.mm" and short format "DD.MM. hh.mm"  
        time_mod = []
        for i in range(len(_time)):
            if len(str(_time[i])) == 1:
                time_mod.append(f"0{_time[i]}")
            else:
                time_mod.append(str(_time[i]))

        return f"{time_mod[2]}.{time_mod[1]}.{time_mod[0]} {time_mod[3]}.{time_mod[4]}", f"{time_mod[2]}.{time_mod[1]}. {time_mod[3]}.{time_mod[4]}"




if __name__ == "__main__": # main block for testing
    print(config)

    w = Wlan()
    w.connect()
    w.get_time()
    print(w.time)
    print("MAC: ", w.mac)