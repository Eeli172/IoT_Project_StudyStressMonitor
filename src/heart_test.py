import time
from heartbeat_animation import HeartAnimation
import hardware  

heart = HeartAnimation(delay=80)

while True:
    heart.next_frame()
    time.sleep_ms(80)