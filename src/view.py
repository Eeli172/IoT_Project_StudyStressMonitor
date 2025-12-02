import hardware
# "display layouts (functions that draw on the OLED)"



def display_center(text_list): # list of rows, max 16 characters / row AND max 6 rows
    hardware.oled.fill(0)
    row_height_px = 10
    char_width_px = 8
    
    y = int((hardware.oled_height - row_height_px*len(text_list))/2) # calculate y-position for the first row to center the whole text horizontally
    for row in text_list:
        x = int((hardware.oled_width - char_width_px*len(row))/2) # center vertically
        hardware.oled.text(row, x, y) 
        y += row_height_px # next row +10px 
        
    hardware.oled.show()

def display_left(text_list): # list of rows, max 16 characters / row AND max 6 rows
    hardware.oled.fill(0)
    row_height_px = 10
    char_width_px = 8
    
    y = int((hardware.oled_height - row_height_px*len(text_list))/2) # calculate y-position for the first row to center the whole text horizontally
    for row in text_list:
        x = int((hardware.oled_width - char_width_px*len(row))/2) # center vertically
        hardware.oled.text(row, 0, y) 
        y += row_height_px # next row +10px 
        
    hardware.oled.show()



def draw_menu(index, items): # menu view by index for pointer and list of menu items - max 6 items
    hardware.oled.fill(0)

    for i in range(len(items)):
        hardware.oled.text(f'{">" if index == i else " "}{items[i]}', 0, int((hardware.oled_height - len(items) * 10) / 2) + i * 10)
        
    hardware.oled.show()




if __name__ == "__main__":


    display_center(["TO START", "MEASUREMENT", "PLACE FINGER", "ON SENSOR", "AND", "PRESS BUTTON"])

