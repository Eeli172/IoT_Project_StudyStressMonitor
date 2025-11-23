import hardware
import micropython
import view

micropython.alloc_emergency_exception_buf(200)   # For hard interrupts


class Menu:
    def __init__(self, oled, items):
        self.oled = oled
        self.items = items
        self.index = 0

    def draw(self):
        view.draw_menu(self.index, self.items)

    def move(self, step):
        self.index += step
        if self.index < 0:
            self.index = len(self.items) - 1
        if self.index >= len(self.items):
            self.index = 0


class App:
    def __init__(self):
        # Display 
        self.oled = hardware.oled

        # Encoder + push button
        self.encoder = hardware.Encoder()
        
        # States
        self.screen = "menu" # current state
        
        # Menu items
        items = ["1. MEASURE HR", "2. BASIC HRV", "3. KUBIOS", "4. HISTORY"]
        self.menu = Menu(self.oled, items)
        

    def run(self):
        self.menu.draw()
        self.screen = "menu"

        while True:
            while self.encoder.fifo.has_data():
                step = self.encoder.fifo.get()
                
                if self.screen == "menu":
                    
                    if step == 1 or step == -1:
                        self.menu.move(step)
                        self.menu.draw()
                        
                    elif step == 0:
                        if self.menu.index == 0:
                            self.screen = "measure_hr"
                            view.display_center(["START","MESAUREMENT","BY PRESSING","BUTTON"])
                        
                    elif self.screen == "measure_hr":
                        if step == 0:
                            self.screen = "menu"
                            self.menu.draw()
                    
                   #elif self.screen == ""
                    
                    

if __name__ == "__main__":
    App().run()
