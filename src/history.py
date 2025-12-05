import ujson
import hardware
import view
import time
from config import config


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
        header = "    DATE   TIME"
        self.pos = self.index // config["rotation_sensivity"] # calculate menu position
        print(self.items)
        view.draw_menu(self.pos, self.items, header) # draw the menu


    def move(self, step): # move in menu - method is called when encoder is turned
        self.index += step
        if self.index < 0:
            self.index = len(self.items) * config["rotation_sensivity"] - 1
        if self.index >= len(self.items) * config["rotation_sensivity"]:
            self.index = 0





class History:
    def __init__(self, encoder):
        self.file = "history.json"      # name of the json file to save the data in
        self.history_size = 3           # amount of saved sessions
        self.sessions = []              # placeholder for sessions
        self.encoder = encoder        # instance of the encoder
        self.oled = hardware.oled
        self.menu = Menu()



    def load_sessions(self):
        try:
            with open(self.file, "r") as f:
                self.sessions = ujson.load(f)   # get the data from the file
                print("LOADED SESSION")
        except (OSError, ValueError):           # file doesn’t exist or is empty/corrupt
            print("SESSION LOADING FAILED ")
            self.sessions = []



    def save_sessions(self):
        with open(self.file, "w") as f:
            ujson.dump(self.sessions, f)        # write the new data into the file



    def add_session(self, new_data):
        self.load_sessions()    # load the sessions from json
        self.sessions.append(new_data)          # add new session

        # if there are more sessions in history than history_size → remove the oldest
        if len(self.sessions) > self.history_size: 
            self.sessions.pop(0)    # remove first element

        self.save_sessions()


    def make_items(self):
        self.menu.items = []
        for i in range(len(self.sessions)):
            self.menu.items.append(f"{i+1}. {self.sessions[(i+1)*(-1)]["timestamp_short"]}")
        self.menu.items.append("BACK")


    def run(self):
        self.load_sessions()
        self.make_items()
        finished = False
        while not finished:
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
                    while self.encoder.button() == 0: # wait until button is released
                        while self.encoder.fifo.has_data(): # drain fifo
                            self.encoder.fifo.get()
                            
                            
                    print(self.menu.pos, len(self.menu.items)-1)
                    if self.menu.pos == len(self.menu.items)-1: # if last option (BACK) of the menu is chosen 
                        finished = True # quit to menu

                    else:
                        view.display_left([
                            str(self.sessions[self.menu.pos*(-1)-1]["timestamp_long"]),
                            "",
                            'MEAN HR:' + str(int(self.sessions[self.menu.pos*(-1)-1]["mean_hr"])),
                            'MEAN PPI:' + str(int(self.sessions[self.menu.pos*(-1)-1]["mean_ppi"])),
                            'RMSSD:' + str(int(self.sessions[self.menu.pos*(-1)-1]["rmssd"])),
                            'SDNN:' + str(int(self.sessions[self.menu.pos*(-1)-1]["sdnn"]))
                        ])

                        while self.encoder.button() == 1: # wait until button is pressed
                            pass


                    while self.encoder.button() == 0: # wait until button is released 
                        while self.encoder.fifo.has_data(): # drain fifo
                            self.encoder.fifo.get()




if __name__ == "__main__":
    e=hardware.Encoder()

    history = History(e)
    history.run()

