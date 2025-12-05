import time
import hardware   

class HeartAnimation:
    def __init__(self, delay=80, offset_x=0, offset_y=0):  # delay in ms
        self.delay = delay
        self.offset_x = offset_x
        self.offset_y = offset_y

        # OLED from hardware
        self.oled = hardware.oled
        self.W = hardware.oled_width
        self.H = hardware.oled_height
        
        # Frames generated from png- pictures 
        # Frame 1 (small heart)      
        self.heart_1 = [
            "000100001000",
            "011110011110",
            "111111111111",
            "111111111111",
            "111111111111",
            "111111111111",
            "011111111110",
            "001111111100",
            "000111111000",
            "000011110000",
            "000001100000",
        ]

        # Frame 2 (medium heart)
        self.heart_2 = [
            "000011000000110000",
            "001111110011111100",
            "011111111111111110",
            "011111111111111110",
            "111111111111111111",
            "111111111111111111",
            "011111111111111110",
            "011111111111111110",
            "001111111111111100",
            "001111111111111100",
            "000111111111111000",
            "000011111111110000",
            "000001111111100000",
            "000000111111000000",
            "000000001100000000",
        ]

        # Frame 3 (large heart)
        self.heart_3 = [
            "0000110000001110000",
            "0011111100011111000",
            "0111111110111111100",
            "1111111111111111110",
            "1111111111111111111",
            "1111111111111111111",
            "1111111111111111111",
            "1111111111111111110",
            "0111111111111111100",
            "0011111111111111100",
            "0011111111111111000",
            "0001111111111110000",
            "0000111111111100000",
            "0000011111111000000",
            "0000001111110000000",
            "0000000011100000000",
        ]

        # Animation sequence, repeat
        self.frames = [self.heart_1, self.heart_2, self.heart_3, self.heart_2]
        self.current = 0

    def draw_pattern(self, pattern):
        h = len(pattern)
        w = len(pattern[0])

        # Heart position: offset_x =0, offset_y =0 --- center
        x0 = (self.W - w) // 2 + self.offset_x
        y0 = (self.H - h) // 2 + self.offset_y

        # Clear screen
        self.oled.fill(0)

        for y, row in enumerate(pattern):
            for x, ch in enumerate(row):
                if ch == "1":
                    self.oled.pixel(x0 + x, y0 + y, 1)

        self.oled.show()

    # Draw next frame without clear() /show()
    def draw_frame_raw(self):
        pattern = self.frames[self.current]

        h = len(pattern)
        w = len(pattern[0])

        x0 = (self.W - w) // 2 + self.offset_x
        y0 = (self.H - h) // 2 + self.offset_y

        for y, row in enumerate(pattern):
            for x, ch in enumerate(row):
                if ch == "1":
                    self.oled.pixel(x0 + x, y0 + y, 1)

        # next frame
        self.current = (self.current + 1) % len(self.frames)

    # Show next animation frame
    def next_frame(self):
        pattern = self.frames[self.current]
        self.draw_pattern(pattern)
        self.current = (self.current + 1) % len(self.frames)

    def run(self, cycles=None):
        #  Infinite loop
        if cycles is None:
            while True:
                self.next_frame()
                time.sleep_ms(self.delay)
        else:
            #  Run animation for N cycles
            for _ in range(cycles * len(self.frames)):
                self.next_frame()
                time.sleep_ms(self.delay)
