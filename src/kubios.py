from mqtt import Mqtt
from config import config
from ppi_list import measure
from view import display_left, display_center
from hardware import Encoder
import time

class Kubios:
    def __init__(self, wlan, encoder):
        self.ppi_list  = []                             # placeholder for ppi_data
        self.mode = "kubios"                            # mode for mqtt instance
        self.wlan = wlan                                # wlan instance
        self.mqtt = Mqtt(self.wlan, self.mode)          # define mqtt instance
        self.topic_pub = config["broker"]["kubios_pub"] # publish topic - (config.json)
        self.topic_sub = config["broker"]["kubios_sub"] # subscribe topic (config.json)
        self.success = 2                                # helper for handling errors (0=allGood;continueProgram, 1=Failed;returnToMenu, 2=Failed;keepTrying)
        self.encoder = encoder                          # encoder instance



    def get_data(self): # gather ppi -data
        self.ppi_list = [1036, 1020, 1008, 952, 996, 1012, 1080, 1004, 940, 960, 980, 1004, 982, 980, 988, 982, 1012, 968, 944, 996, 988, 980, 928, 956, 972, 1004, 988, 888, 900, 956]                    # gather ppi -data
        # self.ppi_list = measure() # measure hr and get list of ppi -values


    def run(self):
        # drain fifo
        self.encoder.drain_fifo()
            
        # plot on oled AND wait until button is pressed
        display_center(["TO START KUBIOS-", "ANALYSIS", "", "1. PLACE THUMB", "ON SENSOR", "2. PRESS BUTTON"])
        button_pressed = False      # helper to tell if user pressed the button or not
        
        while not button_pressed:   # wait for user to be ready to start the measurement
            if self.encoder.fifo.has_data():
                if self.encoder.fifo.get() == 0:
                    button_pressed = True


        # plot on oled AND get ppi data
        display_center(["Collecting", " data.."])
        self.get_data()


        # plot on oled 
        display_center(["Sending data.."])

        # connect to wlan
        self.wlan.connect()


        # plot on oled AND send data to broker AND wait for the results to be returned
        while self.success == 2:
            display_center(["Sending data.."])
            btn = 0 # helper for button press in case of exception
            try:
                result = self.mqtt.run(self.topic_pub, self.topic_sub, self.ppi_list)
                self.success = 0 # program ran succesfully

            except Exception as e: # failed to run program
                print("Failed to run mqtt:".upper(), e)
                display_center(("CONNECTION ERROR", "", "press button to", "retry  OR  wait", "5 sec to return", "to main menu"))

                # drain fifo
                self.encoder.drain_fifo()
                # wait 5 seconds to return to main menu - retry if the button is pressed
                time_beginning = time.ticks_ms()
                while time.ticks_diff(time.ticks_ms(), time_beginning) < 5000 and not btn: # wait 5 seconds
                    if self.encoder.fifo.has_data():
                        if self.encoder.fifo.get() == 0: # button is pressed
                            btn = 1 # continue from the beginning of the loop

                if btn: 
                    print("retry")
                    continue # button pressed - retry
                else: 
                    print("exit loop")
                    self.success = 1 # exit loop -> return main menu
                

        # drain fifo
        self.encoder.drain_fifo()
        if not self.success:
            # plot the results on oled
            display_left([
                f"MEAN HR: {int(result["msg"]["data"]["analysis"]["mean_hr_bpm"])}", 
                f"MEAN PPI: {int(result["msg"]["data"]["analysis"]["mean_rr_ms"])}", 
                f"RMSSD: {int(result["msg"]["data"]["analysis"]["rmssd_ms"])}", 
                f"SDNN: {int(result["msg"]["data"]["analysis"]["sdnn_ms"])}", 
                f"SNS: {result["msg"]["data"]["analysis"]["sns_index"]:.3f}", 
                f"PNS: {result["msg"]["data"]["analysis"]["pns_index"]:.3f}"
            ])


            # return to menu when button is pressed
            button_pressed = False

            while not button_pressed: # show data on oled until button is pressed and program returns to main menu
                if self.encoder.fifo.has_data():
                    while self.encoder.fifo.has_data():
                        if self.encoder.fifo.get() == 0:
                            button_pressed = True


if __name__ == "__main__": # main block for testing
    k = Kubios()
    k.run()