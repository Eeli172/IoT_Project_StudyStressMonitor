import hardware
import micropython
import time
import view
from config import Wlan, config
from kubios import Kubios
from hrv import Hrv
from history import History
from measure_hr import Measure_hr
from logo_animation import LogoAnimation


micropython.alloc_emergency_exception_buf(200)   # For hard interrupts



class Menu:
    def __init__(self):
        self.oled = hardware.oled # instance of oled
        self.items = config["menu_items"] # menu options
        self.index = 0 # encoder's +1's and -1's are added to this variable
        self.pos = 0 # position in menu - index divided by rotation_sensivity defined in config.json
        self.change = True # helper to tell if any change happened; do we need to refresh the oled 


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
        
        # measuring
        self.measure_hr = Measure_hr(self.menu, self.encoder, self.sensor)
        
        # wlan
        self.wlan = Wlan()


    def run(self):
        logo = LogoAnimation(delay = 80) # Show logo animatiom before menu
        logo.run(cycles = 6) # cycles(6) * 4 frame * 80ms = show animation for 1,92 s
        
        while 1:
            if self.menu.change: # refresh menu screen after turning rotary encoder OR when returning back to menu
                self.menu.draw()
                self.menu.change = False
                self.encoder = hardware.Encoder()
                self.measure_hr.encoder = self.encoder
            
            
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
                        self.measure_hr.run()
                                                                

                    elif self.menu.pos == 1: # BASIC HRV ############################
                        Hrv(self.wlan).run()


                    elif self.menu.pos == 2: # KUBIOS ############################
                        Kubios(self.wlan).run()
                            

                    elif self.menu.pos == 3: # HISTORY ############################
                        self.history.run()


                    while not self.encoder.button.value(): # drain fifo before returning to menu
                        while self.encoder.fifo.has_data():
                            self.encoder.fifo.get()


                    

if __name__ == "__main__":# main block for testing
    App().run()
