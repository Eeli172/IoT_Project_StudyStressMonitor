import hardware
import micropython
import time
import view
from config import config
from kubios import Kubios
from hrv import Hrv
from measure import measure
from history import History


micropython.alloc_emergency_exception_buf(200)   # For hard interrupts



class Menu:
    def __init__(self):
        self.oled = hardware.oled # instance of oled
        self.items = config["menu_items"] # menu options
        self.index = 0 # encoder's +1's and -1's are added to this variable
        self.pos = 0 # position in menu - index divided by rotation_sensivity defined in config.json
        self.change = True # helper to tell if any change happened; do we need to refresh the oled 


    def update_items(self, items):
        self.items = items


    def draw(self): 
        self.pos = self.index // config["rotation_sensivity"] # calculate menu position
        view.draw_menu(self.pos, self.items) # draw the menu


    def move(self, step): # move in menu - method is called when encoder is turned
        self.index += step
        if self.index < 0:
            self.index = len(self.items) * config["rotation_sensivity"] - 1
        if self.index >= len(self.items) * config["rotation_sensivity"]:
            self.index = 0



class App:
    def __init__(self):
        # Encoder + push button
        self.encoder = hardware.Encoder()
        
        # Sensor
        self.sensor = hardware.Sensor()
        
        # Menu items
        self.menu = Menu()

        # history
        self.history = History(self.encoder)
        

    def run(self):
        while 1:
            if self.menu.change: # refresh menu screen after turning rotary encoder OR when returning back to menu
                self.menu.draw()
                self.menu.change = False
                self.encoder = hardware.Encoder()
            
            
            if self.encoder.fifo.has_data(): # button pressed OR encoder turned
                step = self.encoder.fifo.get()
                self.menu.change = True # to refresh menu screen on the beginning of the next iteration

                if step != 0: # ENCODER WAS TURNED ############################
                    self.menu.move(step)
                    

                else: # BUTTON WAS PRESSED ############################

                    # make sure fifo is empty and button is released before opening selected menu item
                    time.sleep_ms(50) # debounce
                    while self.encoder.fifo.has_data(): # drain fifo
                        self.encoder.fifo.get()
                    while self.encoder.button() == 0: # wait until button is released
                        time.sleep_ms(10)


                    if self.menu.pos == 0: # MEASURE HR ############################
                        while self.encoder.fifo.has_data():
                            self.encoder.fifo.get()
                        view.display_center(config["screen"][0])
                        time.sleep(1)
                        while not (self.encoder.fifo.has_data() and self.encoder.fifo.get() == 0): # waiting until the user presses the button
                            time.sleep_ms(10)
                        while self.encoder.button() == 0: # wait until button is released
                            time.sleep_ms(10)
                        while self.encoder.fifo.has_data(): # wait until fifo is empty
                            self.encoder.fifo.get()
                            
                        self.sensor.start()
                        result = measure(self.sensor, self.encoder)
                        if result == "abort":
                            self.menu.change = True
                            self.sensor.stop()        
                                                                


                    elif self.menu.pos == 1: # BASIC HRV ############################
                        Hrv().run()


                    elif self.menu.pos == 2: # KUBIOS ############################
                        Kubios().run()
                            

                    elif self.menu.pos == 3: # HISTORY ############################
                        self.history.run()


                    while not self.encoder.button.value(): # drain fifo before returning to menu
                        while self.encoder.fifo.has_data():
                            self.encoder.fifo.get()


                    

if __name__ == "__main__": # main block for testing
    App().run()
