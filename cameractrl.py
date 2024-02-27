"""
cameractrl.py
Python Bottle script for controlling the Pi Camera NOIR, thermal AMG8833 
and IR LEDs
electro-dan.co.uk
based on:
https://funprojects.blog/2020/01/12/pi-rover-using-bottle-web-framework/
https://electronut.in/talking-to-a-raspberry-pi-from-your-phone-using-bottle-python/
"""

from bottle import route, request, run, get, static_file #sudo apt install python3-bottle
from rpi_hardware_pwm import HardwarePWM #sudo pip3 install rpi-hardware-pwm
import dbus
import os
 
ir_leds = HardwarePWM(pwm_channel=0, hz=500000)
ir_on = False
thermal_on = False
ir_leds.start(0)
DUTY_CYCLE = 20 # 0 to 100
THERMAL_SERVICE = "amg8833.service"

# use decorators to link the function to a url
@route('/')
def server_static():
    return static_file("cameractrl.html", root='')

@route('/cameractrl.js')
def server_static():
    return static_file("cameractrl.js", root='')

@route('/cameractrl.css')
def server_static():
    return static_file("cameractrl.css", root='')

@route('/shutdown')
def server_static():
    return static_file("shutdown.html", root='')

# Process an AJAX POST request
@route('/action', method='POST')
def do_action():
    global ir_on
    global thermal_on

    json_request = request.json
    action = json_request.get("action")
    errorMessage = ""
    
    print("Requested action: " + action)
    
    # This method seems to require X11, as well as both services running as user
    #bus = dbus.SessionBus()
    #systemd = bus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
    #manager = dbus.Interface(systemd, 'org.freedesktop.systemd1.Manager')

    if action == "ir":
        if "enabled" in json_request:
            if json_request.get("enabled") == "true":
                ir_on = True
            else:
                ir_on = False
        else:
            # Toggle IR LED state
            ir_on = not ir_on
        
        if ir_on:
            # Enable the IR LEDs by PWM
            ir_leds.change_duty_cycle(DUTY_CYCLE) # duty cycle 0 to 100
        else:
            # Disable the IR LEDs
            ir_leds.change_duty_cycle(0) # duty cycle 0 to 100

    elif action == "thermal":
        if "enabled" in json_request:
            if json_request.get("enabled") == "true":
                thermal_on = True
            else:
                thermal_on = False
        else:
            # Toggle Thermal service state
            thermal_on = not thermal_on
 
        if thermal_on:
            # Start service
            try:
                #manager.StartUnit(THERMAL_SERVICE, 'replace')
                os.system("sudo systemctl start amg8833.service") # Start the service
                thermal_on = True
            except Exception as e:
                errorMessage = f"Failed to start {THERMAL_SERVICE} - {e}.".format()
        else:
            # Stop service
            try:
                #manager.StopUnit(THERMAL_SERVICE, 'replace')
                os.system("sudo systemctl stop amg8833.service") # Stop the service
                thermal_on = False
            except:
                errorMessage = f"Failed to stop {THERMAL_SERVICE} - {e}.".format()

    elif action == "shutdown":
        os.system("sudo shutdown -h +1") # Shutdown in 1 minute

    elif action == "status":
        x = os.system("sudo systemctl status amg8833.service") # Start the user service
        try:
            #manager.GetUnit(THERMAL_SERVICE)
            thermal_on = True if x == 0 else False
        except:
            thermal_on = False
    else:
        errorMessage = "Unknown action"
    
    if errorMessage != "":
        return {'status':'ERROR','message':errorMessage}

    # Always return status
    retIR = "ON" if ir_on else "OFF"
    retThermal = "ON" if thermal_on else "OFF"
    return {'status':'OK','ir_state':retIR, 'thermal_state':retThermal}


run(host = '0.0.0.0', port = '8082')
