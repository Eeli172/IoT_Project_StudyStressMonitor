import hardware



def display_center(list_of_rows): # list of rows, max 16 characters / row AND max 6 rows
    hardware.oled.fill(0) # empty oled
    row_height_px = 10
    char_width_px = 8
    
    y = int((hardware.oled_height - row_height_px*len(list_of_rows))/2) # calculate y-position for the first row to center the whole text horizontally
    for row in list_of_rows:
        x = int((hardware.oled_width - char_width_px*len(row))/2) # center vertically
        hardware.oled.text(row, x, y) 
        y += row_height_px # next row +10px 
        
    hardware.oled.show() # plot on oled




def display_left(list_of_rows): # list of rows, max 16 characters/row AND max 6 rows
    hardware.oled.fill(0) # empty oled
    row_height_px = 10
    
    y = int((hardware.oled_height - row_height_px*len(list_of_rows))/2) # calculate y-position for the first row to center the whole text horizontally
    x = 0
    for row in list_of_rows:
        hardware.oled.text(row, x, y) 
        y += row_height_px # next row +10px 
        
    hardware.oled.show() # plot on oled




def draw_menu(index, items): # menu view by index for pointer and list of menu items - max 6 items
    hardware.oled.fill(0) # empty oled


    for i in range(len(items)): # draw menu options and a cursor next to the right option

        cursor = ">" if index == i else " "

        hardware.oled.text(f'{cursor}{items[i]}', 0, int((hardware.oled_height - len(items) * 10) / 2) + i * 10)
        

    hardware.oled.show() # plot on oled




if __name__ == "__main__": # main block for testing


    display_center(["TO START", "MEASUREMENT", "PLACE FINGER", "ON SENSOR", "AND", "PRESS BUTTON"])

