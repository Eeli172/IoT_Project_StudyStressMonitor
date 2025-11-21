import hardware
import micropython

micropython.alloc_emergency_exception_buf(200)   # For hard interrupts


class Menu:
    def __init__(self, oled, items):
        self.oled = oled
        self.items = items
        self.index = 0

    def draw(self):
        self.oled.fill(0)

        # 1. MEASURE HR
        if self.index == 0:
            self.oled.text(">" + self.items[0], 0, 10)
        else:
            self.oled.text(" " + self.items[0], 0, 10)

        # 2. BASIC HRV 
        if self.index == 1:
            self.oled.text(">" + self.items[1], 0, 20)
        else:
            self.oled.text(" " + self.items[1], 0, 20)

        # 3. KUBIOS
        if self.index == 2:
            self.oled.text(">" + self.items[2], 0, 30)
        else:
            self.oled.text(" " + self.items[2], 0, 30)

        # 4. HISTORY
        if self.index == 3:
            self.oled.text(">" + self.items[3], 0, 40)
        else:
            self.oled.text(" " + self.items[3], 0, 40)

        self.oled.show()

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
        items = [
            "1. MEASURE HR",
            "2. BASIC HRV",
            "3. KUBIOS",
            "4. HISTORY"
        ]
        self.menu = Menu(self.oled, items)
        
    def show_measure_hr_screen(self):
        self.oled.fill(0)
        self.oled.text("      START", 0, 15)
        self.oled.text("   MESAUREMENT", 0, 25)
        self.oled.text("   BY PRESSING", 0, 35)
        self.oled.text("      BUTTON", 0, 45)
#         self.oled.text("TO START", 0, 50)
        self.oled.show()

    def run(self):
        self.menu.draw()
        self.screen = "menu"

        while True:
            while self.encoder.fifo.has_data():
                step = self.encoder.fifo.get()
                
                if self.screen == "menu":
                    print(step, self.screen)
                    
                    if step == 1 or step == -1:
                        self.menu.move(step)
                        self.menu.draw()
                        
                    elif step == 0:
                        if self.menu.index == 0:
                            self.screen = "measure_hr"
                            self.show_measure_hr_screen()
                        
                    elif self.screen == "measure_hr":
                        if step == 0:
                            self.screen = "menu"
                            self.menu.draw()
                    
                   #elif self.screen == ""
                    
                    

if __name__ == "__main__":
    App().run()
