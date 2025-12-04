# HeartRateMonitor


1) What you need
- A Raspberry Pi Pico with MicroPython installed.
- SSD1306 OLED display - CONNECTION: 
    - scl -> pin 15 
    - sda -> pin 14
- A photoplethysmography pulse sensor. Built and tested with Crowtail's model CT010712P - CONNECTION: 
        - data -> pin 26
- A rotary encoder with push button - CONNECTION: 
        - Channel A -> pin 10 
        - Channel B -> pin 11 
        - Button -> pin 12
- A USB cable and a computer.
- Kubios proxy ip/port.
- Wifi ssid and password.
- `mpremote` installed on your computer.

2) config.json
- Open `src/config.json` in a text editor.
- Set `wifi.ssid` and `wifi.password` 
- Set `broker.ip` and `broker.port`

3) Copy the code to the Pico
- Connect the Pico to your computer with USB.
- On your computer navigate into the HeartRateMonitor-folder and run: 
        `install.cmd`   on Windows 
            OR 
        `install.sh`    on Linux/Mac

4) Run the program
- Start the app by restarting your device (Pico)
- Use the rotary encoder and button on the device to choose a menu item:
  - `1. MEASURE HR` — measure heart rate.
  - `2. BASIC HRV`  — compute HRV locally and send a record to mqtt broker to save into a database.
  - `3. KUBIOS`     — send PPI to Kubios proxy and get analysis back -> plot on screen
  - `4. HISTORY`    — locally saved three last measurements to be checked later

5) Debugging tips (if it doesn't work)
- If Wi‑Fi does not connect: check `src/config.json` for typos in SSID/password.
- If Kubios returns `Invalid request.`:
        - Wait 1 second and try again (the server may be busy).
- If you still need help: copy the printed output and share the logs (timestamps and responses).
