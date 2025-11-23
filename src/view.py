import hardware
# "display layouts (functions that draw on the OLED)"


def display_center(text_list): # list of rows, max 16 characters / row AND max 6 rows
    hardware.oled.fill(0)

    y = int((hardware.oled_height - 10*len(text_list))/2) # calculate y-position for the first row to center the whole text horizontally
    for row in text_list:
        x = int((hardware.oled_width - 8*len(row))/2) # center vertically
        hardware.oled.text(row, x, y) 
        y += 10 # next row +10px 
        
    hardware.oled.show()



def draw_menu(index, items): # menu view by index for pointer and list of menu items - max 6 items
    hardware.oled.fill(0)

    for i in range(len(items)):
        hardware.oled.text(f'{">" if index == i else " "}{items[i]}', 0, int((hardware.oled_height - len(items) * 10) / 2) + i * 10)
        
    hardware.oled.show()




if __name__ == "__main__":
    import time


    t = ["123ewg4", "43523454523", "fdaf aefaf feeww", "234324"]
    display_center(t)

    for i in range(4):
        time.sleep(0.5)
        items = [
            "1. MEASURE HR",
            "2. BASIC HRV",
            "3. KUBIOS",
            "4. HISTORY"
        ]
        draw_menu(i, items)