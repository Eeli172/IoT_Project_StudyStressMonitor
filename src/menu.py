import hardware
import micropython
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
            
            
            if self.encoder.fifo.has_data(): # button pressed or rotary encoder turned
                step = self.encoder.fifo.get()
                self.menu.change = True # refresh menu screen on the beginning of the next iteration

                if step != 0: # rotary encoder was turned
                    self.menu.move(step)
                    

                else: # button was pressed
                    while not self.menu.back: # button not pressed

                        if self.menu.pos == 0: # MEASURE HR
                            view.display_center(config["screen_hr"])


                        if self.menu.pos == 1: # BASIC HRV
                            view.display_center(config["screen_hrv"])


                        if self.menu.pos == 2: # KUBIOS
                            view.display_center(config["screen_kubios"])
                            # TEST VALUES
                            ppi_list = [828, 836, 852, 760, 800, 796, 856, 824, 808, 776, 724, 816, 800, 812, 812, 812, 756, 820, 812, 800] #TEST VALUES

                            kubios = Kubios(ppi_list)
                            received_data = kubios.run()
                            self.menu.back = True
                                

                            # TEST PRINT 
                            print(received_data["msg"]) 



                        if self.menu.pos == 3: # HISTORY
                            view.display_center(config["screen_history"])


                        if self.encoder.fifo.has_data(): # BACK TO MENU

                            if self.encoder.fifo.get() == 0: # button pressed

                                self.menu.back = True





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
