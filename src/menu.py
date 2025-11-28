import hardware
import micropython
import time
import view
from config import config
from kubios import Kubios


micropython.alloc_emergency_exception_buf(200)   # For hard interrupts



class Menu:
    def __init__(self, oled, items):
        self.oled = oled
        self.items = items
        self.index = 0
        self.pos = 0 
        self.back = False
        self.change = True

    def draw(self):
        self.pos = self.index // config["rotation_sensivity"]
        view.draw_menu(self.pos, self.items)

    def move(self, step):
        self.index += step
        if self.index < 0:
            self.index = len(self.items) * config["rotation_sensivity"] - 1
        if self.index >= len(self.items) * config["rotation_sensivity"]:
            self.index = 0



class App:
    def __init__(self):
        # Display 
        self.oled = hardware.oled

        # Encoder + push button
        self.encoder = hardware.Encoder()
        
        # States
        # self.screen = "menu" # current state
        
        # Menu items
        self.menu = Menu(self.oled, config["menu_items"])
        

    def run(self):
        while 1:
            if self.menu.change: # refresh menu screen after turning rotary encoder OR when returning back to menu
                self.menu.draw()
                self.menu.change = False
                self.menu.back = False
            
            
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
                        view.display_center(config["screen"][0])



                    if self.menu.pos == 1: # BASIC HRV ############################
                        view.display_center(config["screen"][1])



                    if self.menu.pos == 2: # KUBIOS ############################
                        view.display_center(config["screen"][2])

                        # TEST VALUES
                        ppi_list = [828, 836, 852, 760, 800, 796, 856, 824, 808, 776, 724, 816, 800, 812, 812, 812, 756, 820, 812, 800] #TEST VALUES

                        kubios = Kubios(ppi_list)
                        received_data = kubios.run()
                        self.menu.back = True
                            
                        # TEST PRINT 
                        print(received_data["msg"]) 



                    if self.menu.pos == 3: # HISTORY ############################
                        view.display_center(config["screen"][3])



                    while self.encoder.fifo.has_data(): # drain fifo before returning to menu
                        self.encoder.fifo.get()




        # self.menu.draw()
        # self.screen = "menu"

        # while True:
        #     while self.encoder.fifo.has_data():
        #         step = self.encoder.fifo.get()
                
        #         if self.screen == "menu":
                    
        #             if step != 0:
        #                 self.menu.move(step)

        #                 self.menu.draw()
                        
        #             elif step == 0:
        #                 if self.menu.pos == 0:
        #                     self.screen = "measure_hr"
        #                     view.display_center(config["screen_hr"])
                    
        #            #elif self.screen == ""

                
                    

if __name__ == "__main__":
    App().run()
